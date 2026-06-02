from __future__ import annotations

import pytest

from azan_mcp.tools.dua_dhikr import (
    _get_counter_recommendation_impl,
    _get_dua_by_topic_impl,
    _get_evening_adhkar_impl,
    _get_morning_adhkar_impl,
    _get_prayer_dua_impl,
    _list_dua_topics_impl,
    _search_dua_impl,
)


def test_morning_adhkar_count():
    result = _get_morning_adhkar_impl()
    items = result["data"]
    assert len(items) >= 10


def test_morning_adhkar_fields():
    result = _get_morning_adhkar_impl()
    for item in result["data"]:
        assert "arabic" in item, f"Missing arabic: {item['id']}"
        assert "source" in item, f"Missing source: {item['id']}"
        assert "count" in item, f"Missing count: {item['id']}"
        assert item["category"] == "morning"


def test_morning_adhkar_sorted():
    result = _get_morning_adhkar_impl()
    orders = [item["order"] for item in result["data"]]
    assert orders == sorted(orders)


def test_evening_adhkar_count():
    result = _get_evening_adhkar_impl()
    assert len(result["data"]) >= 10


def test_list_dua_topics():
    result = _list_dua_topics_impl()
    topics = result["data"]
    assert len(topics) >= 15
    for required in ("travel", "eating", "sleeping", "anxiety", "forgiveness"):
        assert required in topics, f"Missing topic: {required}"


def test_get_dua_by_topic_travel():
    result = _get_dua_by_topic_impl("travel")
    assert len(result["data"]) >= 1
    for dua in result["data"]:
        assert "arabic" in dua
        assert "source" in dua


def test_get_dua_by_topic_eating():
    result = _get_dua_by_topic_impl("eating")
    assert len(result["data"]) >= 1


def test_get_dua_by_topic_unknown_raises():
    with pytest.raises(ValueError, match="Unknown topic"):
        _get_dua_by_topic_impl("nonexistent_xyz_topic")


def test_get_dua_by_topic_error_lists_available():
    with pytest.raises(ValueError, match="travel"):  # "travel" appears in available list
        _get_dua_by_topic_impl("nonexistent_xyz_topic")


def test_search_dua_finds_results():
    result = _search_dua_impl("travel")
    assert len(result["data"]) > 0


def test_search_dua_has_matched_fields():
    result = _search_dua_impl("bismillah")
    for item in result["data"]:
        assert "matched_fields" in item
        assert len(item["matched_fields"]) > 0


def test_search_dua_respects_limit():
    result = _search_dua_impl("allah", limit=3)
    assert len(result["data"]) <= 3


def test_search_dua_empty_query_raises():
    with pytest.raises(ValueError, match="empty"):
        _search_dua_impl("   ")


def test_counter_recommendation_valid():
    result = _get_counter_recommendation_impl("morning_001")
    d = result["data"]
    assert "count" in d
    assert d["count"] >= 1


def test_counter_recommendation_unknown_raises():
    with pytest.raises(ValueError, match="not found"):
        _get_counter_recommendation_impl("nonexistent_999")


def test_prayer_dua_ruku():
    result = _get_prayer_dua_impl("ruku")
    assert len(result["data"]) >= 1
    for item in result["data"]:
        assert "arabic" in item
        assert "source" in item


def test_prayer_dua_all_positions():
    for pos in ("ruku", "sujood", "tashahhud", "after_salah"):
        result = _get_prayer_dua_impl(pos)
        assert len(result["data"]) >= 1


def test_prayer_dua_invalid_position():
    with pytest.raises(ValueError, match="position"):
        _get_prayer_dua_impl("invalid_position")


def test_meta_has_disclaimer():
    result = _get_morning_adhkar_impl()
    assert "source" in result["meta"]
    assert "scholar" in result["meta"]["source"].lower()
