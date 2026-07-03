# CLAW Refactoring Proposals and Optimization Analysis

**Date:** 2024-06-19
**Project:** CLAW (ClawSpring)
**Version:** V01

## 1. Executive Summary
This document outlines specific performance bottlenecks and areas of code duplication identified during the optimization audit. The focus is on reducing startup latency, minimizing repetitive I/O, and improving overall system responsiveness through lazy loading and efficient caching.

## 2. Performance Bottlenecks

### 2.1 Startup Latency (Monolithic Imports)
**Issue:** Modules like `01_SRC/core.py` and `01_SRC/providers.py` import heavy dependencies (e.g., `rich`, `anthropic`, `openai`, `urllib.request`) at the top level. This triggers a cascade of imports that slows down the initial execution of `run_claw.py`.
**Recommendation:**
- Use lazy loading for third-party SDKs.
- Move `import anthropic` and `import openai` inside the respective `stream_*` functions.
- Move `rich` related imports into a deferred initialization block in `core.py`.

### 2.2 Repetitive I/O (Task and Memory Stores)
**Issue:**
- `01_SRC/task/store.py`: The `_load()` function is called at the beginning of every public API method (`create_task`, `get_task`, `update_task`, etc.). While it has a `_loaded` flag, it doesn't account for external changes efficiently and still represents a pattern that could be improved by using a persistent session-level object.
- `01_SRC/memory/store.py`: `load_entries()` performs a full directory scan (`glob("*.md")`) and reads every file to parse frontmatter on every search or index load.
**Recommendation:**
- Implement an in-memory singleton for the Task Store that only reloads if the file's `mtime` changes.
- Cache memory frontmatter metadata in a lightweight index file (improving upon the current `MEMORY.md` which is mostly for LLM context) to avoid reading all `.md` files on every search.

### 2.3 Repeated File System Scans (Context Injection)
**Issue:** `01_SRC/context.py` calls `get_git_info()` and `get_claude_md()` frequently. Although it has a basic cache, the TTL is hardcoded and the mechanism is fragmented.
**Recommendation:**
- Standardize a `TTL_Cache` utility in `00_SOPORTE/utils.py`.
- Apply this cache to all "environment discovery" functions.

## 3. Code Duplication

### 3.1 Frontmatter Parsing
**Issue:** Both `memory/store.py` and some documentation tools implement manual string splitting for YAML-like frontmatter.
**Recommendation:** Create a centralized `parse_frontmatter(text)` utility in a shared file (e.g., `01_SRC/error_utils.py` or a new `01_SRC/fs_utils.py`).

### 3.2 Dynamic Import Handling
**Issue:** There are multiple `importlib.import_module` calls scattered across `config.py` and various tests to handle nomenclature constraints.
**Recommendation:** Centralize dynamic loading logic in `00_SOPORTE/config.py` or a dedicated loader utility that abstracts the nomenclature details.

### 3.3 Path Resolution Logic
**Issue:** Multiple modules manually implement "walk up to find `.git` or `CLAUDE.md`" logic.
**Recommendation:** Add a `find_project_root()` and `get_project_file(name)` helper to a centralized utility module.

## 4. Refactoring Roadmap (Suggested)

| Phase | Task | Impact |
| :--- | :--- | :--- |
| **Phase 1** | Implement lazy loading for SDKs in `providers.py` and `core.py`. | High (Startup Speed) |
| **Phase 2** | Refactor `task/store.py` and `memory/store.py` to use `mtime` based caching. | Medium (Responsiveness) |
| **Phase 3** | Consolidate environment discovery logic in `context.py`. | Medium (CPU overhead) |
| **Phase 4** | Centralize FS utilities (Frontmatter, Root Discovery). | High (Maintainability) |

## 5. Implementation Notes
- **Constraint:** Do not modify the general P.A.R.A. architecture.
- **Constraint:** Maintain ISO-SAGE nomenclature for any new utility files.
- **Goal:** Reduce `run_claw.py --version` execution time by >30%.
