# Duplicate Logic Report — CLAW

## 1. Duplicated Modules

| Module A | Module B | Similarity | Status |
| :--- | :--- | :--- | :--- |
| `01_SRC/2024-06-19_CLAW_CORE_V01.py` | `01_SRC/2024-06-19_CLAW_CLAWSPRING_V02.py` | ~98% | Redundant |
| `01_SRC/2024-06-19_CLAW_CORE_V01.py` | `01_SRC/2024-06-19_CLAW_CLAWSPRING_CORE_V01.py` | ~95% | Redundant |
| `01_SRC/2024-06-19_CLAW_AGENT_V01.py` | `01_SRC/2024-06-19_CLAW_AGENT_CORE_V01.py` | 100% | Identical |
| `01_SRC/memory.py` | `01_SRC/memory_shim.py` | 100% | Link/Shim |

## 2. Duplicated Functions (Logic Mirroring)

The following functions are implemented nearly identically across the three "Core" modules:
- `repl(config, initial_prompt)`
- `run_query(user_input, is_background)`
- `handle_slash(line, state, config)`
- All slash commands: `cmd_model`, `cmd_config`, `cmd_save`, `cmd_load`, `cmd_tasks`, `cmd_ssj`, etc.
- UI Helpers: `info`, `ok`, `warn`, `err`, `clr`, `render_diff`.
- Streaming helpers: `stream_text`, `stream_thinking`, `flush_response`.

## 3. Estimated Maintenance Cost

**HIGH.**
- **Synchronous Updates**: Any improvement to the REPL (e.g., adding a new slash command or fixing a bug in the Telegram bridge) requires manual copy-pasting across 3 files totaling over 9,000 lines of code.
- **Risk of Divergence**: `CLAWSPRING_V02` already contains specific Windows UTF-8 fixes (Bug #4) and model support improvements that are missing or implemented differently in `CORE_V01`. This creates inconsistent behavior depending on the entry point used.
- **Import Confusion**: Multiple entry points and shims make it difficult to determine the canonical source of truth for the "Agent" and "Provider" logic.

## 4. Proposed Future Consolidation

1.  **Extract REPL Core**: Move the REPL loop, input handling, and slash command dispatcher to a shared `01_SRC/base_repl.py`.
2.  **Modularize Commands**: Move `cmd_*` implementations to a `01_SRC/commands/` directory to keep the main loops clean and easily extensible.
3.  **Unify Agent**: Delete `2024-06-19_CLAW_AGENT_CORE_V01.py` and point all imports to `agent.py` (which links to `2024-06-19_CLAW_AGENT_V01.py`).
4.  **Single Entry Point**: Converge on `run_claw.py` as the only entry point, which imports a single, consolidated `core` module. Distinct "personalities" can be handled via configuration rather than file duplication.
5.  **Remove Shims**: Once imports are standardized to use the symlinks (e.g., `import agent` instead of `import 2024-06-19_CLAW_AGENT_V01`), remove the redundant `*_shim.py` files.
