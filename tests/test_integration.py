"""Integration tests — spin up the MCP server via stdio and call tools."""
from __future__ import annotations

import os
import pytest
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


FIXTURES_DIR = Path(__file__).parent / "fixtures"
CONFIG_PATH  = str(FIXTURES_DIR / "makkah-config.json")

SERVER_PARAMS = StdioServerParameters(
    command="python",
    args=["-m", "azan_mcp.server"],
    env={**os.environ, "AZAN_CONFIG": CONFIG_PATH},
)


@pytest.mark.asyncio
async def test_server_lists_tools():
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            tool_names = [t.name for t in tools_result.tools]
            for expected in (
                "get_prayer_times",
                "get_next_prayer",
                "get_qibla_direction",
                "get_hijri_date",
                "get_morning_adhkar",
                "calculate_zakat",
                "get_asma_ul_husna",
                "get_server_info",
            ):
                assert expected in tool_names, f"Tool '{expected}' not found in server"


@pytest.mark.asyncio
async def test_get_server_info():
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_server_info", {})
            assert result.content
            import json
            data = json.loads(result.content[0].text)
            assert data["data"]["calculation_method"] == "umm_al_qura"


@pytest.mark.asyncio
async def test_get_prayer_times():
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_prayer_times", {"date": "2024-03-01"})
            assert result.content
            import json
            data = json.loads(result.content[0].text)
            assert "fajr" in data["data"]


@pytest.mark.asyncio
async def test_get_hijri_date():
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_hijri_date", {"date": "2024-03-01"})
            assert result.content
            import json
            data = json.loads(result.content[0].text)
            assert data["data"]["hijri_year"] == 1445
