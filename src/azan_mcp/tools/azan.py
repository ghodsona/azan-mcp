"""Azan and Iqama tools — Epic 3."""
from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from mcp.server.fastmcp import FastMCP

from azan_mcp.config import get_config
from azan_mcp.prayer_engine import compute_prayer_times

logger = logging.getLogger(__name__)

VALID_PRAYERS = ("fajr", "dhuhr", "asr", "maghrib", "isha")

AZAN_LINES = [
    {"arabic": "اللهُ أَكْبَر", "transliteration": "Allahu Akbar", "count": 4},
    {"arabic": "أَشْهَدُ أَنْ لَا إِلَهَ إِلَّا اللهُ", "transliteration": "Ashhadu an la ilaha illallah", "count": 2},
    {"arabic": "أَشْهَدُ أَنَّ مُحَمَّدًا رَسُولُ اللهِ", "transliteration": "Ashhadu anna Muhammadan rasulullah", "count": 2},
    {"arabic": "حَيَّ عَلَى الصَّلَاة", "transliteration": "Hayya alas-salah", "count": 2},
    {"arabic": "حَيَّ عَلَى الْفَلَاح", "transliteration": "Hayya alal-falah", "count": 2},
    {"arabic": "الصَّلَاةُ خَيْرٌ مِنَ النَّوْم", "transliteration": "As-salatu khayrun minan-nawm", "count": 2, "fajr_only": True},
    {"arabic": "اللهُ أَكْبَر", "transliteration": "Allahu Akbar", "count": 2},
    {"arabic": "لَا إِلَهَ إِلَّا اللهُ", "transliteration": "La ilaha illallah", "count": 1},
]


def _validate_prayer(prayer: str) -> str:
    p = prayer.lower()
    if p not in VALID_PRAYERS:
        raise ValueError(f"prayer must be one of: {', '.join(VALID_PRAYERS)}. Got: {prayer!r}")
    return p


def _meta() -> dict:
    cfg = get_config()
    return {
        "calculation_method": cfg.calculation_method.value,
        "madhab": cfg.madhab.value,
        "confidence_key": "high=Bukhari/Muslim, medium=Abu Dawud/Tirmidhi/Nasai/Ibn Majah, low=weak chains",
        "generated_at": datetime.now(ZoneInfo("UTC")).isoformat(),
    }


def _get_azan_text_impl(prayer: str, language: str = "both") -> dict:
    p = _validate_prayer(prayer)
    if language not in ("arabic", "transliteration", "both"):
        raise ValueError("language must be 'arabic', 'transliteration', or 'both'")
    lines = [line for line in AZAN_LINES if not line.get("fajr_only") or p == "fajr"]
    result = []
    for line in lines:
        entry: dict = {"count": line["count"]}
        if language in ("arabic", "both"):
            entry["arabic"] = line["arabic"]
        if language in ("transliteration", "both"):
            entry["transliteration"] = line["transliteration"]
        result.append(entry)
    return {
        "data": {
            "prayer": p.capitalize(),
            "lines": result,
            "note": "The Fajr Azan includes 'As-salatu khayrun minan-nawm' (Prayer is better than sleep) twice after Hayya alal-falah.",
        },
        "meta": _meta(),
    }


def _get_iqama_time_impl(prayer: str, date_str: str | None = None) -> dict:
    p = _validate_prayer(prayer)
    cfg = get_config()
    from datetime import date
    from zoneinfo import ZoneInfo as ZI
    d = date.fromisoformat(date_str) if date_str else datetime.now(ZI(cfg.timezone)).date()
    times = compute_prayer_times(cfg.latitude, cfg.longitude, d, cfg.calculation_method.value, cfg.madhab.value, cfg.timezone)
    from datetime import timedelta
    offset = cfg.iqama_offsets.get(p, 10)
    iqama_time = times[p] + timedelta(minutes=offset)
    return {
        "data": {
            "prayer":     p.capitalize(),
            "adhan_time": times[p].isoformat(),
            "iqama_time": iqama_time.isoformat(),
            "offset_minutes": offset,
        },
        "meta": _meta(),
    }


def _set_iqama_offset_impl(prayer: str, offset_minutes: int) -> dict:
    p = _validate_prayer(prayer)
    if offset_minutes < 0:
        raise ValueError(f"offset_minutes must be non-negative, got {offset_minutes}")
    cfg = get_config()
    cfg.iqama_offsets[p] = offset_minutes
    return {
        "data": {
            "updated_prayer": p.capitalize(),
            "new_offset_minutes": offset_minutes,
            "all_offsets": dict(cfg.iqama_offsets),
            "note": "This offset is stored in memory only and resets when the server restarts.",
        },
        "meta": _meta(),
    }


def _get_daily_azan_schedule_impl() -> dict:
    cfg = get_config()
    from datetime import date, timedelta
    from zoneinfo import ZoneInfo as ZI
    today = datetime.now(ZI(cfg.timezone)).date()
    times = compute_prayer_times(cfg.latitude, cfg.longitude, today, cfg.calculation_method.value, cfg.madhab.value, cfg.timezone)
    schedule = []
    for prayer in ("fajr", "dhuhr", "asr", "maghrib", "isha"):
        offset = cfg.iqama_offsets.get(prayer, 10)
        from datetime import timedelta
        iqama = times[prayer] + timedelta(minutes=offset)
        schedule.append({
            "prayer":     prayer.capitalize(),
            "adhan_time": times[prayer].isoformat(),
            "iqama_time": iqama.isoformat(),
            "offset_minutes": offset,
        })
    return {"data": schedule, "meta": _meta()}


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def get_azan_text(prayer: str, language: str = "both") -> dict:
        """Return the full Azan text. prayer: fajr, dhuhr, asr, maghrib, isha. language: arabic, transliteration, or both."""
        return _get_azan_text_impl(prayer, language)

    @mcp.tool()
    def get_iqama_time(prayer: str, date: str | None = None) -> dict:
        """Return the Iqama time (adhan + configured offset) for a given prayer. prayer: fajr, dhuhr, asr, maghrib, isha."""
        return _get_iqama_time_impl(prayer, date)

    @mcp.tool()
    def set_iqama_offset(prayer: str, offset_minutes: int) -> dict:
        """Update the Iqama offset (minutes after adhan) for a prayer. Change is in-memory only and resets on server restart."""
        return _set_iqama_offset_impl(prayer, offset_minutes)

    @mcp.tool()
    def get_daily_azan_schedule() -> dict:
        """Return today's complete Azan schedule: adhan time and iqama time for all 5 daily prayers."""
        return _get_daily_azan_schedule_impl()
