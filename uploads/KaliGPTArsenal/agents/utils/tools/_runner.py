#!/usr/bin/env python3

# /agents/utils/tools/_runner.py
# Shared subprocess runner for KaliGPT security tool wrappers.
# Provides binary availability checks, timeouts, argument validation and a single
# uniform result schema so the AI agent receives parseable dictionaries instead
# of raw, ambiguous text.


import logging
import shutil
import subprocess

logger = logging.getLogger("kaligpt.tools")


# Every tool wrapper returns at least these keys, so the model can rely on a
# stable schema. Wrappers may add tool-specific keys (e.g. "hosts", "findings").
BASE_RESULT_KEYS = ("success", "installed", "command", "returncode", "output", "error")

# Characters that must never appear inside a single tool argument such as a
# target host/url. Commands are executed WITHOUT a shell (argument lists), so
# these cannot cause shell injection, but rejecting them early catches obvious
# mistakes and malformed input before a tool is launched.
_FORBIDDEN_ARG_CHARS = set(";&|`$><\n\r\t \"'\\")


def _result(success, installed=None, command="", returncode=None,
            output=None, error=None, **extra) -> dict:
    """Build a result dict that always carries the base schema keys."""
    result = {
        "success": success,
        "installed": installed,
        "command": command,
        "returncode": returncode,
        "output": output,
        "error": error,
    }
    result.update(extra)
    return result


def tool_available(binary: str) -> bool:
    """
    Check whether a command-line tool/binary is installed and on PATH.
    """
    return shutil.which(binary) is not None


def validate_arg(value: str) -> bool:
    """
    Validate a single command argument (e.g. a target host or URL).

    Returns True if the value is safe to pass as a single argument,
    False if it is empty or contains forbidden / shell-meta characters.
    """
    if not value or not isinstance(value, str):
        return False
    return not any(ch in _FORBIDDEN_ARG_CHARS for ch in value)


def invalid_arg(name: str, value) -> dict:
    """
    Build a uniform error result for an invalid/rejected argument.
    """
    return _result(False, error=f"Invalid {name}: {value!r}")


def missing_dependency(binary: str) -> dict:
    """
    Build a uniform error result when a required tool/binary is not installed.
    """
    return _result(
        False,
        installed=False,
        error=f"'{binary}' is not installed or not in PATH. "
              f"Install it (e.g. 'sudo apt install {binary}') to use this tool.",
    )


def run_command(args: list, timeout: int = 120, input_text: str = None) -> dict:
    """
    Run a command (as an argument list, no shell) and return a structured result.

    Args:
        args (list[str]): Command and its arguments, e.g. ["nmap", "-sV", "host"].
        timeout (int): Maximum seconds to wait before aborting. (default = 120)
        input_text (str | None): Optional text piped to the process stdin.

    Returns:
        dict -> {
            success: bool,            # True only if the binary ran AND returncode == 0
            installed: bool,          # whether the binary was found on PATH
            command: str,             # the command line that was executed
            returncode: int | None,
            output: str | None,       # stdout
            error: str | None         # stderr or a runner-level error message
        }
    """
    if not args:
        return _result(False, installed=False, error="No command provided")

    binary = args[0]
    command = " ".join(str(a) for a in args)

    if not tool_available(binary):
        logger.debug("Tool not available: %s", binary)
        return missing_dependency(binary)

    try:
        proc = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            input=input_text,
        )
        logger.debug("Ran %r -> returncode=%s", command, proc.returncode)
        return _result(
            success=proc.returncode == 0,
            installed=True,
            command=command,
            returncode=proc.returncode,
            output=proc.stdout,
            error=proc.stderr.strip() or None,
        )

    except subprocess.TimeoutExpired:
        logger.warning("Command timed out after %ss: %s", timeout, command)
        return _result(False, installed=True, command=command,
                       error=f"Command timed out after {timeout}s")

    except Exception as exc:
        logger.error("Execution error for %s: %s", command, exc)
        return _result(False, installed=True, command=command,
                       error=f"Execution error: {exc}")
