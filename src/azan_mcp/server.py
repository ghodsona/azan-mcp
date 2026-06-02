"""Azan-MCP server entry point."""
from __future__ import annotations

import logging
import sys

from mcp.server.fastmcp import FastMCP

from azan_mcp.tools import azan, asma, calculators, calendar, dua_dhikr, prayer_times

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    "Azan MCP",
    instructions=(
        "Islamic utilities server. Provides prayer times, Qibla direction, "
        "Islamic calendar, Azan/Iqama scheduling, Du'a & Dhikr, Zakat calculators, "
        "and the 99 Names of Allah. All times are timezone-aware. "
        "Use get_server_info to check the active location and calculation method."
    ),
)

prayer_times.register(mcp)
azan.register(mcp)
calendar.register(mcp)
dua_dhikr.register(mcp)
calculators.register(mcp)
asma.register(mcp)


def main() -> None:
    logger.info("Starting Azan-MCP server")
    mcp.run()


if __name__ == "__main__":
    main()
