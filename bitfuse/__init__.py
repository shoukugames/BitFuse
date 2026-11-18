"""BitFuse - learn binary numbers by flicking switches and lighting fireworks."""
__version__ = "0.1.0"
RELEASE_DATE = "2026-11-05"

# True when running in a web browser (pygbag / WebAssembly).
import sys as _sys
WEB = _sys.platform == "emscripten"
