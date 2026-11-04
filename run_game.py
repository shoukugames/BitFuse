#!/usr/bin/env python3
"""Start BitFuse.  Options: --windowed, --version, --smoke-test <file>"""
import sys

from bitfuse.app import main

if __name__ == "__main__":
    sys.exit(main())
