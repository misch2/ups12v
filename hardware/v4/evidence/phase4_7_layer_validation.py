"""Deprecated Phase4.7 entry point; use hardware/v4/tools/kicad_v4.py."""
def main():
    from pathlib import Path
    import sys
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
    from v4kicad.cli import main as toolkit_main
    return toolkit_main(["validate", *sys.argv[1:]])

if __name__ == "__main__":
    raise SystemExit(main())
