"""
Package initialization for the spanner_agent.

This package exposes the `root_agent` instance so that the Agent Development Kit
can discover it automatically when scanning the directory.  Without an
`__init__.py` file, Python will not treat `spanner_agent` as a package and the
ADK may fail to locate your agent.

Upon import, this file simply imports the `agent` module which defines the
`root_agent`.  Having a side‑effecting import is acceptable here because the
ADK expects the agent to be defined at import time.
"""

from . import agent  # noqa: F401
