"""Entry point for ``python -m protocols``."""

from __future__ import annotations

import sys

from protocols.cli import main

if __name__ == "__main__":
    sys.exit(main())
