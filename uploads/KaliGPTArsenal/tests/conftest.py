"""
Pytest configuration for KaliGPT.

The tools package imports a few heavy third-party libraries at module load time
(`requests`, `bs4`, `newspaper`, `rich`). They are not needed to exercise the
Kali tool wrappers, so we install lightweight stubs for any that are missing.
This keeps the test suite runnable in a minimal environment (and in CI before
the full runtime requirements are installed).
"""

import sys
import types
from pathlib import Path

# Make the repository root importable (so `import agents...` works).
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _stub(name: str, **attrs) -> None:
    """Register a stub module only if the real one cannot be imported."""
    try:
        __import__(name)
        return
    except ModuleNotFoundError:
        # Only stub genuinely missing modules; let real import-time errors
        # (e.g. a broken dependency) propagate instead of masking them.
        module = types.ModuleType(name)
        for key, value in attrs.items():
            setattr(module, key, value)
        sys.modules[name] = module


class _RequestException(Exception):
    pass


_stub(
    "requests",
    get=lambda *a, **k: None,
    request=lambda *a, **k: None,
    RequestException=_RequestException,
    exceptions=types.SimpleNamespace(RequestException=_RequestException),
)
_stub("bs4", BeautifulSoup=object)
_stub("newspaper", Article=type("Article", (), {}), Config=object)

# rich is only needed by sibling modules pulled in via agents/__init__.py.
for _name in ("rich", "rich.console", "rich.markdown", "rich.panel",
              "rich.syntax", "rich.table"):
    _stub(_name)
# Provide the attributes the agents package references at import time.
sys.modules["rich.console"].Console = type(
    "Console", (), {"__init__": lambda self, *a, **k: None, "width": 80}
)
sys.modules["rich.markdown"].Markdown = object
sys.modules["rich.panel"].Panel = object
sys.modules["rich.syntax"].Syntax = object
sys.modules["rich.table"].Table = object
