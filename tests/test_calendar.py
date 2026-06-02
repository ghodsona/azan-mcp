from __future__ import annotations

from datetime import date

import pytest

from azan_mcp.tools.calendar import (
    _convert_gregorian_to_hijri_impl,
    _convert_hijri_to_gregorian_impl,
    _get_eid_dates_impl,
    _get_hijri_date_impl,
    _get_islamic_events_impl,
    _get_ramadan_dates_impl,
    _get_voluntary_fasting_dates_impl,
)


def test_gregorian_to_hijri_known():
    """2024-03-01 → ~20 Sha'ban 1445 AH (tabular ±1 day tolerance)."""
    result = _convert_gregorian_to_hijri_impl(2024, 3, 1)
    h = result["data"]
    assert h["hijri_year"] == 1445
    assert h["hijri_month"] == 8  # Sha'ban
    assert abs(h["hijri_day"] - 20) <= 1, f"Expected ~20, got {h['hijri_day']}"
    assert h["hijri_month_name"] == "Sha'ban"
    assert "AH" in h["formatted"]


def test_hijri_to_gregorian_known():
    """1 Ramadan 1445 → ~2024-03-11 or 12."""
    result = _convert_hijri_to_gregorian_impl(1445, 9, 1)
    g = result["data"]
    assert g["year"] == 2024
    assert g["month"] == 3
    assert abs(g["day"] - 11) <= 1
    assert "iso" in g


def test_hijri_gregorian_round_trip():
    result1 = _convert_gregorian_to_hijri_impl(2024, 6, 15)
    h = result1["data"]
    result2 = _convert_hijri_to_gregorian_impl(h["hijri_year"], h["hijri_month"], h["hijri_day"])
    g = result2["data"]
    assert g["year"] == 2024
    assert g["month"] == 6
    assert abs(g["day"] - 15) <= 1


def test_get_hijri_date_defaults_to_today():
    result = _get_hijri_date_impl()
    h = result["data"]
    assert 1300 < h["hijri_year"] < 1600
    assert 1 <= h["hijri_month"] <= 12
    assert 1 <= h["hijri_day"] <= 30


def test_get_islamic_events_returns_events():
    result = _get_islamic_events_impl(1445)
    events = result["data"]
    assert len(events) >= 11
    names = [e["name"] for e in events]
    assert "Eid al-Fitr" in names
    assert "Eid al-Adha" in names
    assert "Start of Ramadan" in names


def test_get_islamic_events_filter_by_month():
    result = _get_islamic_events_impl(1445, hijri_month=9)
    events = result["data"]
    assert all(e["hijri_date"].startswith(str(e["hijri_date"].split()[0])) for e in events)
    names = [e["name"] for e in events]
    assert "Start of Ramadan" in names


def test_ramadan_dates_2024():
    result = _get_ramadan_dates_impl(2024)
    data = result["data"]
    start = date.fromisoformat(data["start"])
    assert start.year == 2024
    assert start.month == 3
    assert data["hijri_year"] == 1445


def test_eid_dates_2024():
    result = _get_eid_dates_impl(2024)
    data = result["data"]
    fitr = date.fromisoformat(data["eid_al_fitr"])
    adha = date.fromisoformat(data["eid_al_adha"])
    assert fitr.year == 2024
    assert adha.year == 2024
    assert fitr.month in (4,)  # April
    assert adha.month in (6, 7)  # June or July


def test_voluntary_fasting_ramadan_month():
    result = _get_voluntary_fasting_dates_impl(2024, 3)  # Ramadan 2024
    days = result["data"]
    assert len(days) > 0
    reasons_flat = [r for day in days for r in day["reasons"]]
    # Should have Mondays and/or Thursdays
    assert any("Monday" in r or "Thursday" in r for r in reasons_flat)


def test_calendar_meta_has_disclaimer():
    result = _get_hijri_date_impl()
    assert "note" in result["meta"] or "disclaimer" in result["meta"]
    assert result["meta"]["confidence"] == "medium"
