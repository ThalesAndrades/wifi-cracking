---
name: kali-arsenal
description: >-
  Build, extend, and validate KaliGPT's security tool wrappers (the agent's Kali
  arsenal). Use when adding a new Kali/recon/web/network/offensive tool to
  agents/utils/tools, when fixing or reviewing an existing wrapper, when wiring a
  tool into the registry, or when the user mentions nmap/nuclei/ffuf/sqlmap/etc.
  wrappers, the tool runner, the dual-use authorization gate, or the tool tests.
---

# KaliGPT — Kali Arsenal Skill

This skill encodes the conventions for KaliGPT's agent tool wrappers so every new
tool is safe, structured, testable, and discoverable. Follow it whenever you add
or change a tool under `agents/utils/tools/`.

## Mental model

The agent can already run anything via `execute_generic_linux_command`. Raw
command output is hard for an LLM to reason about, so each first-class tool is a
**thin wrapper** that:

1. validates its arguments,
2. runs the binary through the shared runner (no shell, with a timeout),
3. parses the output into a structured `dict`,
4. is registered with a category so it shows up in `/list tools`.

Never shell out directly from a wrapper. Always go through `_runner.run_command`.

## The shared runner (`agents/utils/tools/_runner.py`)

| Helper | Use it for |
|--------|------------|
| `validate_arg(value)` | Reject empty / shell-meta / whitespace args. Call on every user-controlled arg. |
| `run_command(args, timeout=…, input_text=None)` | Execute `args` (a list, never a string) without a shell. Returns the base schema. |
| `tool_available(binary)` | Check a binary exists before a multi-step flow. |
| `invalid_arg(name, value)` | Uniform error result for a rejected argument. |
| `missing_dependency(binary)` | Uniform error result when a binary is absent. |
| `_result(success, …, **extra)` | Build a result carrying the base schema + tool-specific keys. |

**Base result schema** (always present): `success`, `installed`, `command`,
`returncode`, `output`, `error`. Wrappers add their own keys (e.g. `hosts`,
`findings`, `open_ports`).

## Recipe: add a new tool

1. Pick the right module: `kali_recon.py`, `kali_web.py`, `kali_network.py`, or
   `kali_offensive.py` (create a new one only for a genuinely new category).
2. Write the function:
   - First docstring line = the agent-facing description (keep it one sentence).
   - Type hints must be explicit `T | None` — never implicit Optional (Ruff RUF013).
   - Validate each user arg with `validate_arg`; return `invalid_arg(...)` on failure.
   - Build the args list, call `run_command`, then parse `result["output"]`.
   - Wrap parsing in `try/except` and log failures via
     `logging.getLogger("kaligpt.tools").debug(...)`; never raise.
3. Register it in `agents/utils/tools/__init__.py` by adding the function to the
   right `TOOL_CATEGORIES` entry. Everything else (flat list, metadata,
   `/list tools`) derives from that mapping automatically.
4. Add it to the table in `requirements/globals.md`.
5. Add tests in `tests/` (see below).

### Skeleton

```python
def my_tool(target: str, flag: str | None = None, timeout: int = 120) -> dict:
    """One-line description shown to the agent."""
    if not validate_arg(target):
        return invalid_arg("target", target)
    args = ["mytool", target]
    if flag:
        if not validate_arg(flag):
            return invalid_arg("flag", flag)
        args += ["--flag", flag]
    result = run_command(args, timeout=timeout)
    parsed = []
    if result.get("output"):
        try:
            parsed = parse(result["output"])
        except ValueError as exc:
            logger.debug("mytool parse failed: %s", exc)
    result["items"] = parsed
    return result
```

## Dual-use / offensive tools

Anything that attacks rather than observes (injection, brute-force, cracking)
lives in `kali_offensive.py` and MUST:

- take an `authorized: bool = False` parameter and return `_refused()` unless it
  is `True` (the gate makes the model deliberate; it is not a hard security
  boundary),
- still validate inputs after the gate,
- be listed in `DUAL_USE_TOOLS` in `__init__.py` so `/list tools` flags it.

Identification-only helpers (e.g. `hash_identify`) are NOT gated.

## Don't inject flags

Do not splat user-provided flag strings into argv. For options that change tool
behavior (e.g. nmap scan type), map a small **allowlist** of named profiles to
fixed flag lists (see `NMAP_PROFILES`) and reject anything else. This keeps
output parsing consistent and blocks NSE/output-altering flags.

## Tests (`tests/`)

- `tests/conftest.py` stubs heavy deps (`requests`, `bs4`, `newspaper`, `rich`)
  so the suite runs in a minimal env.
- Test parsers by monkeypatching the module's `run_command` to return canned
  output — never invoke a real tool in a test.
- Cover: argument validation, the auth gate (refused vs. validated), output
  parsing, and the registry/metadata counts.
- Run with `pytest -q`. The dispatch workflow also runs this on every trigger.

## Validate before committing

```bash
python -m py_compile agents/utils/tools/*.py
pytest -q
```

Keep author/header comment style consistent with the surrounding files. Do not
add a `claude-*` model id or attribution to any committed file.
