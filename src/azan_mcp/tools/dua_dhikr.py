"""Du'a and Dhikr tools — Epic 5."""
from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from mcp.server.fastmcp import FastMCP

from azan_mcp.data import load_adhkar, load_duas

logger = logging.getLogger(__name__)

_ADHKAR: list[dict] = load_adhkar()
_DUAS_BY_TOPIC: dict[str, list[dict]] = {
    t["topic"]: t["duas"] for t in load_duas()
}

META_DISCLAIMER = "Authentic hadith collections. Verify with a qualified Islamic scholar."
CONFIDENCE_KEY = "high=Bukhari/Muslim, medium=Abu Dawud/Tirmidhi/Nasai/Ibn Majah, low=weak chains"

PRAYER_DUAS: dict[str, list[dict]] = {
    "ruku": [
        {
            "arabic": "سُبْحَانَ رَبِّيَ الْعَظِيم",
            "transliteration": "Subhana Rabbiyal-'Azim",
            "translation": "Glory be to my Lord, the Most Great.",
            "count": 3,
            "source": "Abu Dawud 869",
            "confidence": "medium",
        }
    ],
    "sujood": [
        {
            "arabic": "سُبْحَانَ رَبِّيَ الْأَعْلَى",
            "transliteration": "Subhana Rabbiyal-A'la",
            "translation": "Glory be to my Lord, the Most High.",
            "count": 3,
            "source": "Abu Dawud 871",
            "confidence": "medium",
        },
        {
            "arabic": "اللَّهُمَّ اغْفِرْ لِي ذَنْبِي كُلَّهُ دِقَّهُ وَجِلَّهُ",
            "transliteration": "Allahumma-ghfir li dhanbi kullahu diqqahu wa jillahu",
            "translation": "O Allah, forgive me all my sins, the small and the great.",
            "count": 1,
            "source": "Sahih Muslim 483",
            "confidence": "high",
        },
    ],
    "tashahhud": [
        {
            "arabic": "التَّحِيَّاتُ لِلَّهِ وَالصَّلَوَاتُ وَالطَّيِّبَاتُ، السَّلَامُ عَلَيْكَ أَيُّهَا النَّبِيُّ وَرَحْمَةُ اللَّهِ وَبَرَكَاتُهُ، السَّلَامُ عَلَيْنَا وَعَلَى عِبَادِ اللَّهِ الصَّالِحِينَ، أَشْهَدُ أَنْ لَا إِلَهَ إِلَّا اللَّهُ وَأَشْهَدُ أَنَّ مُحَمَّدًا عَبْدُهُ وَرَسُولُهُ",
            "transliteration": "At-tahiyyatu lillahi was-salawatu wat-tayyibat. As-salamu 'alayka ayyuhan-nabiyyu wa rahmatullahi wa barakatuh. As-salamu 'alayna wa 'ala 'ibadillahis-salihin. Ashhadu an la ilaha illallah wa ashhadu anna Muhammadan 'abduhu wa rasuluh.",
            "translation": "All greetings, prayers, and pure words are for Allah. Peace be upon you, O Prophet, and the mercy of Allah and His blessings. Peace be upon us and upon the righteous servants of Allah. I bear witness that there is no god but Allah, and I bear witness that Muhammad is His servant and messenger.",
            "count": 1,
            "source": "Sahih al-Bukhari 831",
            "confidence": "high",
        }
    ],
    "after_salah": [
        {
            "arabic": "أَسْتَغْفِرُ اللهَ",
            "transliteration": "Astaghfirullah",
            "translation": "I seek forgiveness from Allah.",
            "count": 3,
            "source": "Sahih Muslim 591",
            "confidence": "high",
        },
        {
            "arabic": "سُبْحَانَ اللهِ",
            "transliteration": "SubhanAllah",
            "translation": "Glory be to Allah.",
            "count": 33,
            "source": "Sahih Muslim 595",
            "confidence": "high",
        },
        {
            "arabic": "الْحَمْدُ لِلَّهِ",
            "transliteration": "Alhamdulillah",
            "translation": "Praise be to Allah.",
            "count": 33,
            "source": "Sahih Muslim 595",
            "confidence": "high",
        },
        {
            "arabic": "اللهُ أَكْبَر",
            "transliteration": "Allahu Akbar",
            "translation": "Allah is the Greatest.",
            "count": 34,
            "source": "Sahih Muslim 595",
            "confidence": "high",
        },
    ],
}


def _meta() -> dict:
    return {
        "source": META_DISCLAIMER,
        "confidence_key": CONFIDENCE_KEY,
        "generated_at": datetime.now(ZoneInfo("UTC")).isoformat(),
    }


def _get_morning_adhkar_impl() -> dict:
    items = sorted(
        [e for e in _ADHKAR if e["category"] == "morning"],
        key=lambda x: x.get("order", 999),
    )
    return {"data": items, "meta": _meta()}


def _get_evening_adhkar_impl() -> dict:
    items = sorted(
        [e for e in _ADHKAR if e["category"] == "evening"],
        key=lambda x: x.get("order", 999),
    )
    return {"data": items, "meta": _meta()}


def _list_dua_topics_impl() -> dict:
    return {
        "data": sorted(_DUAS_BY_TOPIC.keys()),
        "meta": _meta(),
    }


def _get_dua_by_topic_impl(topic: str) -> dict:
    if topic not in _DUAS_BY_TOPIC:
        available = ", ".join(sorted(_DUAS_BY_TOPIC.keys()))
        raise ValueError(f"Unknown topic: {topic!r}. Available topics: {available}")
    return {"data": _DUAS_BY_TOPIC[topic], "meta": _meta()}


def _search_dua_impl(query: str, limit: int = 10) -> dict:
    if not query.strip():
        raise ValueError("query must not be empty")
    if limit < 1:
        raise ValueError("limit must be at least 1")
    q = query.lower()
    fields = ("arabic", "transliteration", "translation")
    results = []
    # Search adhkar
    for entry in _ADHKAR:
        matched = [f for f in fields if q in entry.get(f, "").lower()]
        if matched:
            results.append({**entry, "matched_fields": matched})
    # Search duas
    for topic, duas in _DUAS_BY_TOPIC.items():
        for dua in duas:
            matched = [f for f in fields if q in dua.get(f, "").lower()]
            if not matched and q in topic.lower():
                matched = ["topic"]
            if matched:
                results.append({**dua, "topic": topic, "matched_fields": matched})
    return {"data": results[:limit], "meta": _meta()}


def _get_counter_recommendation_impl(dhikr_id: str) -> dict:
    for entry in _ADHKAR:
        if entry["id"] == dhikr_id:
            return {
                "data": {
                    "id":      entry["id"],
                    "arabic":  entry.get("arabic", ""),
                    "count":   entry["count"],
                    "virtues": entry.get("virtues", ""),
                    "source":  entry.get("source", ""),
                },
                "meta": _meta(),
            }
    raise ValueError(f"Dhikr ID not found: {dhikr_id!r}. Use get_morning_adhkar or get_evening_adhkar to find valid IDs.")


def _get_prayer_dua_impl(position: str) -> dict:
    valid = ("ruku", "sujood", "tashahhud", "after_salah")
    if position not in valid:
        raise ValueError(f"position must be one of: {', '.join(valid)}. Got: {position!r}")
    return {"data": PRAYER_DUAS[position], "meta": _meta()}


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def get_morning_adhkar() -> dict:
        """Return the complete set of morning adhkar (Adhkar al-Sabah) with Arabic, transliteration, translation, source, and recommended count."""
        return _get_morning_adhkar_impl()

    @mcp.tool()
    def get_evening_adhkar() -> dict:
        """Return the complete set of evening adhkar (Adhkar al-Masa) with Arabic, transliteration, translation, source, and recommended count."""
        return _get_evening_adhkar_impl()

    @mcp.tool()
    def list_dua_topics() -> dict:
        """List all available du'a topic slugs that can be used with get_dua_by_topic."""
        return _list_dua_topics_impl()

    @mcp.tool()
    def get_dua_by_topic(topic: str) -> dict:
        """Return all du'a entries for a given topic. Use list_dua_topics to see available topics (e.g. travel, eating, anxiety, sleeping)."""
        return _get_dua_by_topic_impl(topic)

    @mcp.tool()
    def search_dua(query: str, limit: int = 10) -> dict:
        """Search across all du'a and adhkar by Arabic text, transliteration, translation, or topic. Returns matched entries with which fields matched."""
        return _search_dua_impl(query, limit)

    @mcp.tool()
    def get_counter_recommendation(dhikr_id: str) -> dict:
        """Return the recommended repetition count and virtues for a specific dhikr by its ID."""
        return _get_counter_recommendation_impl(dhikr_id)

    @mcp.tool()
    def get_prayer_dua(position: str) -> dict:
        """Return du'as for a specific position in salah. position: ruku, sujood, tashahhud, after_salah."""
        return _get_prayer_dua_impl(position)
