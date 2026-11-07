"""Explicit CLI entry point; importing this file performs no work."""
import sys
from v4kicad.cli import main

if __name__ == '__main__':
    sys.dont_write_bytecode = True
    raise SystemExit(main())
