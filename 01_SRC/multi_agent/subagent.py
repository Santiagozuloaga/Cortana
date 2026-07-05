"""Sub-agent execution: independent agent tasks with optional git isolation."""
from __future__ import annotations

import os
import subprocess
import tempfile
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


# ── Agent definition ───────────────────────────────────────────────────────

@dataclass
class AgentDefinition:
    """Configuration for a specialized agent type."""
    name: str
    description: str
    source: str  # e.g. "built-in", "custom", "~/.clawspring/agents"
    model: Optional[str] = None  # override the default model
    system_prompt: Optional[str] = None  # override the system prompt
    tools: Optional[list[str]] = None  # allowed tools (None = all)


# ── Agent definitions (placeholder) ───────────────────────────────────────

def load_agent_definitions() -> Dict[str, AgentDefinition]:
    """Load agent type definitions from built-in and custom sources."""
    return {}


def get_agent_definition(name: str) -> Optional[AgentDefinition]:
    """Look up an agent definition by name."""
    defs = load_agent_definitions()
    return defs.get(name)


# ── Sub-agent task ────────────────────────────────────────────────────────

@dataclass
class SubAgentTask:
    """Represents a running or completed sub-agent task."""
    id: str
    prompt: str
    status: str = "pending"  # pending | running | completed | failed
    result: Optional[str] = None
    name: str = ""
    worktree_branch: Optional[str] = None
    worktree_path: Optional[str] = None


# ── Git utilities ──────────────────────────────────────────────────────────

def _create_worktree(base_dir: str) -> tuple:
    """Create a temporary git worktree.

    Returns:
        (worktree_path, branch_name)
    Raises:
        subprocess.CalledProcessError or OSError on failure.
    """
    branch = f"nano-agent-{uuid.uuid4().hex[:8]}"
    # mkdtemp gives us a path; remove the empty dir so git can create it
    wt_path = tempfile.mkdtemp(prefix="nano-agent-wt-")
    os.rmdir(wt_path)
    subprocess.run(
        ["git", "worktree", "add", "-b", branch, wt_path],
        cwd=base_dir, check=True, capture_output=True, text=True,
    )
    return wt_path, branch


def _remove_worktree(wt_path: str, branch: str, base_dir: str) -> None:
    """Remove a git worktree and delete its branch (best-effort)."""
    try:
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path],
            cwd=base_dir, capture_output=True,
        )
    except Exception:
        pass
    try:
        subprocess.run(
            ["git", "branch", "-D", branch],
            cwd=base_dir, capture_output=True,
        )
    except Exception:
        pass


# ── Internal helpers ───────────────────────────────────────────────────────

def _agent_run(prompt, state, config, system_prompt, depth=0, cancel_check=None):
    """Lazy-import wrapper to avoid circular dependency with agent module.

    Uses absolute import so this works whether called from inside or outside
    the multi_agent package (sys.path includes the project root).
    """
    import agent as _agent_mod
    return _agent_mod.run(prompt, state, config, system_prompt, depth=depth, cancel_check=cancel_check)


def _extract_final_text(messages):
    """Walk backwards through messages, return first assistant content string."""
    for msg in reversed(messages):
        if msg.get("role") == "assistant" and msg.get("content"):
            return msg["content"]
    return None


# ── SubAgentManager ────────────────────────────────────────────────────────

class SubAgentManager:
    """Manages concurrent sub-agent tasks using a thread pool."""

    def __init__(self, max_concurrent: int = 5, max_depth: int = 5):
        self.tasks: Dict[str, SubAgentTask] = {}
        self._by_name: Dict[str, str] = {}   # name → task_id
        self.max_concurrent = max_concurrent
        self.max_depth = max_depth
        self._pool = ThreadPoolExecutor(max_workers=max_concurrent)

    def spawn(
        self,
        prompt: str,
        config: dict,
        system_prompt: str,
        depth: int = 0,
        agent_def: Optional[AgentDefinition] = None,
        isolation: str = "",     # "" | "worktree"
        name: str = "",
    ) -> SubAgentTask:
        """Spawn a new sub-agent task.

        Args:
            prompt:       user message for the sub-agent
            config:       agent configuration dict (copied before modification)
            system_prompt: base system prompt
            depth:        current nesting depth (prevents infinite recursion)
            agent_def:    optional AgentDefinition with model/system_prompt/tools overrides
            isolation:    "" for normal, "worktree" for isolated git worktree
            name:         optional human-readable task name

        Returns:
            SubAgentTask (with status="pending", waiting for executor)
        """
        if depth >= self.max_depth:
            task = SubAgentTask(
                id=str(uuid.uuid4()),
                prompt=prompt,
                status="failed",
                result=f"Max nesting depth ({self.max_depth}) reached.",
                name=name or "[unnamed]",
            )
            self.tasks[task.id] = task
            return task

        task_id = str(uuid.uuid4())
        task = SubAgentTask(
            id=task_id,
            prompt=prompt,
            name=name or f"agent-{task_id[:8]}",
        )

        if name:
            self._by_name[name] = task_id

        self.tasks[task_id] = task

        # Submit to thread pool
        self._pool.submit(
            self._run_task,
            task,
            config,
            system_prompt,
            depth,
            agent_def,
            isolation,
        )

        return task

    def _run_task(
        self,
        task: SubAgentTask,
        config: dict,
        system_prompt: str,
        depth: int,
        agent_def: Optional[AgentDefinition],
        isolation: str,
    ) -> None:
        """Run a sub-agent task (called in executor thread)."""
        try:
            task.status = "running"

            # Apply agent definition overrides
            if agent_def:
                if agent_def.model:
                    config = {**config, "model": agent_def.model}
                if agent_def.system_prompt:
                    system_prompt = agent_def.system_prompt
                if agent_def.tools:
                    config = {**config, "_allowed_tools": agent_def.tools}

            # Handle git isolation
            if isolation == "worktree":
                try:
                    wt_path, branch = _create_worktree(".")
                    task.worktree_path = wt_path
                    task.worktree_branch = branch
                    # Update config to use worktree
                    config = {**config, "_worktree_dir": wt_path}
                except Exception as e:
                    task.status = "failed"
                    task.result = f"Failed to create worktree: {e}"
                    return

            # Run agent
            try:
                from agent import AgentState
                state = AgentState()
                output_parts = []

                for event in _agent_run(
                    task.prompt, state, config, system_prompt, depth=depth + 1
                ):
                    if hasattr(event, "text"):
                        output_parts.append(event.text)

                task.result = "".join(output_parts) or "(no output)"
                task.status = "completed"

            except Exception as e:
                task.status = "failed"
                task.result = f"Agent execution error: {e}"

        finally:
            # Cleanup worktree
            if task.worktree_path and task.worktree_branch:
                try:
                    _remove_worktree(task.worktree_path, task.worktree_branch, ".")
                except Exception:
                    pass

    def wait(self, task_id: str, timeout: int = 300) -> None:
        """Block until a task completes (with timeout)."""
        task = self.tasks.get(task_id)
        if not task:
            return

        start = time.time()
        while task.status in ("pending", "running"):
            if time.time() - start > timeout:
                task.status = "failed"
                task.result = f"Task timeout ({timeout}s)"
                break
            time.sleep(0.1)

    def send_message(self, target: str, message: str) -> bool:
        """Send a message to a running agent (by name or task_id).
        Returns True if queued, False otherwise.
        """
        # Simplified: placeholder for message queue implementation
        task_id = self._by_name.get(target, target)
        task = self.tasks.get(task_id)
        return task is not None and task.status == "running"

    def list_tasks(self) -> list[SubAgentTask]:
        """Return all tasks."""
        return list(self.tasks.values())
