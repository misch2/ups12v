"""Monitored native entry point for the owner-authorized Phase4.24W wrapper."""
import sys
from v4kicad.stencil_production import main

if __name__=='__main__':
    sys.dont_write_bytecode=True
    main()
