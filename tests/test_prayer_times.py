from __future__ import annotations

from datetime import date

import pytest

from azan_mcp.prayer_engine import (
    bearing_to_cardinal,
    compute_prayer_times,
    qibla_bearing,
)
from azan_mcp.tools.prayer_times import (
    _get_next_prayer_impl,
    _get_prayer_times_impl,
    _get_qibla_direction_impl,
    _get_time_until_next_prayer_impl,
    _get_monthly_prayer_calendar_impl,
    _get_server_info_impl,
    _list_calculation_methods_impl,
)

MAKKAH_LAT = 21.3891
MAKKAH_LNG = 39.8579
LONDON_LAT = 51.5074
LONDON_LNG = -0.1278
TEST_DATE = date(2024, 3, 1)


def test_fajr_makkah_umm_al_qura():
    """Fajr for Makkah on 2024-03-01 with Umm al-Qura should be ~05:27 AST."""
    times = compute_prayer_times(MAKKAH_LAT, MAKKAH_LNG, TEST_DATE, "umm_al_qura", "shafi", "Asia/Riyadh")
    fajr = times["fajr"]
    assert fajr.hour == 5, f"Expected Fajr hour 5, got {fajr.strftime('%H:%M')}"
    assert abs(fajr.minute - 27) <= 3, f"Fajr was {fajr.strftime('%H:%M')}, expected ~05:27"


def test_all_prayer_keys_present():
    times = compute_prayer_times(MAKKAH_LAT, MAKKAH_LNG, TEST_DATE, "umm_al_qura", "shafi", "Asia/Riyadh")
    assert set(times.keys()) == {"fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"}


def test_all_times_timezone_aware():
    times = compute_prayer_times(MAKKAH_LAT, MAKKAH_LNG, TEST_DATE, "umm_al_qura", "shafi", "Asia/Riyadh")
    for name, dt in times.items():
        assert dt.tzinfo is not None, f"{name} datetime must be timezone-aware"


def test_prayer_order():
    """Prayers must be in chronological order."""
    times = compute_prayer_times(MAKKAH_LAT, MAKKAH_LNG, TEST_DATE, "umm_al_qura", "shafi", "Asia/Riyadh")
    order = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]
    for i in range(len(order) - 1):
        assert times[order[i]] < times[order[i + 1]], (
            f"{order[i]} ({times[order[i]]}) must be before {order[i+1]} ({times[order[i+1]]})"
        )


def test_qibla_london():
    """Qibla from London should be ~119° (SE)."""
    bearing = qibla_bearing(LONDON_LAT, LONDON_LNG)
    assert abs(bearing - 119) <= 3, f"Qibla bearing {bearing:.1f}° expected ~119°"


def test_qibla_cardinal_london():
    bearing = qibla_bearing(LONDON_LAT, LONDON_LNG)
    cardinal = bearing_to_cardinal(bearing)
    assert cardinal in ("SE", "SSE", "ESE"), f"Expected SE cardinal, got {cardinal}"


def test_all_10_methods_produce_valid_times():
    from azan_mcp.prayer_engine import METHOD_PARAMS
    for method in METHOD_PARAMS:
        times = compute_prayer_times(MAKKAH_LAT, MAKKAH_LNG, TEST_DATE, method, "shafi", "Asia/Riyadh")
        assert len(times) == 6, f"Method {method} returned {len(times)} prayers"


def test_get_prayer_times_tool_response_shape():
    result = _get_prayer_times_impl("2024-03-01")
    assert "data" in result
    assert "meta" in result
    data = result["data"]
    for prayer in ("fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"):
        assert prayer in data
        assert "T" in data[prayer]  # ISO 8601 format


def test_get_next_prayer_returns_valid_name():
    result = _get_next_prayer_impl()
    assert result["data"]["prayer"] in ("Fajr", "Dhuhr", "Asr", "Maghrib", "Isha")
    assert "time" in result["data"]


def test_get_time_until_next_prayer():
    result = _get_time_until_next_prayer_impl()
    data = result["data"]
    assert "minutes_until" in data
    assert "human_readable" in data
    assert data["minutes_until"] >= 0


def test_get_qibla_direction_tool():
    result = _get_qibla_direction_impl(LONDON_LAT, LONDON_LNG)
    assert "bearing" in result["data"]
    assert "cardinal" in result["data"]
    assert abs(result["data"]["bearing"] - 119) <= 3


def test_monthly_prayer_calendar_length():
    result = _get_monthly_prayer_calendar_impl(2024, 3)
    assert len(result["data"]) == 31  # March has 31 days


def test_get_server_info():
    result = _get_server_info_impl()
    data = result["data"]
    assert "latitude" in data
    assert "calculation_method" in data
    assert data["calculation_method"] == "umm_al_qura"


def test_list_calculation_methods():
    result = _list_calculation_methods_impl()
    assert len(result["data"]) == 10
    ids = [m["id"] for m in result["data"]]
    assert "umm_al_qura" in ids
    assert "mwl" in ids
