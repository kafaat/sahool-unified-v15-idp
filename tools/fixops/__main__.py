"""Allow running fixops as: python -m tools.fixops"""
import asyncio
import sys

from tools.fixops.cli import main

sys.exit(asyncio.run(main()))
