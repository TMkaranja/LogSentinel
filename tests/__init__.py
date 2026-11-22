"""LogSentinel test package.

Makes the ``src/`` layout importable for ``python -m unittest discover``
without installation (no external tooling allowed at runtime or for tests).
"""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
