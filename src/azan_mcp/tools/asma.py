"""Asma ul-Husna (99 Names of Allah) tools — Epic 7."""
from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from mcp.server.fastmcp import FastMCP

from azan_mcp.data import load_asma_ul_husna

logger = logging.getLogger(__name__)

_ASMA: list[dict] = load_asma_ul_husna()
_ASMA_BY_NUMBER: dict[int, dict] = {entry["number"]: entry for entry in _ASMA}


def _meta() -> dict:
    return {
        "source": "Al-Tirmidhi 3507, Sahih al-Bukhari 2736",
        "note": "The 99 Names are derived from the Quran and authentic Sunnah.",
        "confidence_key": "high=Bukhari/Muslim, medium=Abu Dawud/Tirmidhi/Nasai/Ibn Majah, low=weak chains",
        "generated_at": datetime.now(ZoneInfo("UTC")).isoformat(),
    }


def _get_asma_ul_husna_impl() -> dict:
    return {"data": _ASMA, "meta": _meta()}


def _get_name_of_allah_impl(identifier: str | int) -> dict:
    # By number
    if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
        n = int(identifier)
        if n not in _ASMA_BY_NUMBER:
            raise ValueError(f"Name number must be 1–99, got {n}")
        return {"data": _ASMA_BY_NUMBER[n], "meta": _meta()}
    # By transliteration (partial, case-insensitive)
    q = str(identifier).lower()
    matches = [e for e in _ASMA if q in e["transliteration"].lower()]
    if not matches:
        raise ValueError(f"No name found matching: {identifier!r}. Use get_asma_ul_husna to browse all 99 names.")
    return {"data": matches[0] if len(matches) == 1 else matches, "meta": _meta()}


def _search_asma_ul_husna_impl(query: str) -> dict:
    if not query.strip():
        raise ValueError("query must not be empty")
    q = query.lower()
    fields = ("arabic", "transliteration", "meaning", "explanation")
    results = []
    for entry in _ASMA:
        matched = [f for f in fields if q in entry.get(f, "").lower()]
        if matched:
            results.append({**entry, "matched_fields": matched})
    return {"data": results, "meta": _meta()}


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def get_asma_ul_husna() -> dict:
        """Return all 99 Names of Allah (Asma ul-Husna) with Arabic, transliteration, meaning, and explanation."""
        return _get_asma_ul_husna_impl()

    @mcp.tool()
    def get_name_of_allah(identifier: str) -> dict:
        """Look up a specific Name of Allah by number (1–99) or transliteration (e.g. 'Ar-Rahman' or 'rahman')."""
        return _get_name_of_allah_impl(identifier)

    @mcp.tool()
    def search_asma_ul_husna(query: str) -> dict:
        """Search the 99 Names of Allah by meaning, transliteration, or Arabic text."""
        return _search_asma_ul_husna_impl(query)
