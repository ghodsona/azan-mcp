# Azan-MCP

![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![MCP](https://img.shields.io/badge/MCP-FastMCP-brightgreen.svg)
![Tools](https://img.shields.io/badge/Tools-34%20Islamic%20Tools-green.svg)
![Tests](https://img.shields.io/badge/Tests-62%20passing-brightgreen.svg)
![PyPI](https://img.shields.io/badge/PyPI-azan--mcp-blue.svg)
![Hijri](https://img.shields.io/badge/Calendar-Hijri%20%2B%20Gregorian-orange.svg)
![Methods](https://img.shields.io/badge/Calculation-10%20Methods-lightgrey.svg)

**Azan-MCP** is an open-source [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that brings a comprehensive suite of Islamic utilities directly into AI assistants such as Claude Desktop. It enables any LLM client that supports MCP to answer Islamic questions with accuracy, proper sourcing, and full awareness of the user's location, timezone, and madhab.


### What it does

- **Prayer Times** — Calculates the five daily prayers (Fajr, Dhuhr, Asr, Maghrib, Isha) plus Sunrise for any location on Earth using the full Meeus solar algorithm. Supports 10 internationally recognised calculation methods and both Hanafi and Shafi madhab for Asr. Also computes Qibla direction, monthly calendars, and Sunnah prayer windows (Duha, Awwabin, Tahajjud).

- **Azan & Iqama** — Returns the full Azan text in Arabic and transliteration (with the Fajr Tatwidh variant), calculates Iqama times based on configurable per-prayer offsets, and provides a complete daily Azan schedule.

- **Islamic Calendar** — Converts dates between Gregorian and Hijri calendars, lists named Islamic events with their Gregorian equivalents, and identifies recommended voluntary fasting days (Mondays/Thursdays, Ayyam al-Beed, 6 days of Shawwal, Day of Arafah).

- **Du'a & Dhikr** — Provides sourced morning and evening adhkar, du'a collections across 15 topics (travel, eating, anxiety, protection, and more), and du'as for every position in salah. Every entry is traced to its hadith reference with a confidence rating.

- **Zakat & Islamic Calculators** — Calculates Zakat due on cash, gold, silver, and trade goods; determines Nisab thresholds; computes Suhoor/Iftar times for Ramadan date ranges; and distributes inheritance according to Faraid (Quran 4:11-12) using exact fractional arithmetic with Aul handling.

- **99 Names of Allah** — The complete Asma ul-Husna with Arabic text, transliteration, meaning, and explanation for all 99 names, fully searchable.

---


![MCP Architecture](MCP%20image.png)


### Design principles

| Principle | How it is applied |
|-----------|------------------|
| **Accuracy** | Prayer engine implements the full Meeus astronomical algorithm (±2 min vs IslamicFinder). Hijri conversion uses the `hijridate` library. |
| **Authenticity** | Every Du'a and Dhikr entry carries a hadith source reference and a confidence level (`high` = Bukhari/Muslim, `medium` = Sunan books). |
| **Transparency** | All tool responses include a `meta` block stating the calculation method, madhab, source, and confidence used. |
| **Discoverability** | Tools like `list_dua_topics` and `list_calculation_methods` prevent the LLM from guessing invalid inputs. |
| **Safety** | Zakat, Faraid, and calendar tools include a "consult a qualified scholar" disclaimer in every response. |
| **Zero friction** | Installable with a single `uvx azan-mcp` command — no npm, no Docker, no manual setup. |

### Tech Stack

Built with **Python 3.12+** and **FastMCP** (the official Anthropic MCP SDK). The prayer time engine is vendored directly from the Meeus algorithm using Python's standard library only (`math`, `datetime`, `zoneinfo`) — no stale third-party astronomical dependency. The Hijri calendar uses the actively maintained `hijridate` package.

### Folder Structure
```
src/azan_mcp/
├── server.py          # FastMCP entry point — 34 tools across 6 modules
├── config.py          # UserConfig dataclass (location, timezone, method, madhab)
├── prayer_engine.py   # Vendored Meeus solar algorithm
├── tools/             # One module per epic: prayer_times, azan, calendar,
│                      #   dua_dhikr, calculators, asma
└── data/              # adhkar.json · duas.json · asma_ul_husna.json
```

---

## Supported Calculation Methods

| ID | Name | Fajr° | Isha |
|----|------|-------|------|
| `umm_al_qura` | Umm al-Qura, Makkah | 18.5 | 90 min after Maghrib |
| `mwl` | Muslim World League | 18 | 17° |
| `isna` | ISNA | 15 | 15° |
| `egypt` | Egyptian General Authority | 19.5 | 17.5° |
| `karachi` | Univ. of Islamic Sciences, Karachi | 18 | 18° |
| `tehran` | Univ. of Tehran | 17.7 | 14° |
| `kuwait` | Kuwait | 18 | 17.5° |
| `uoif` | UOIF (France) | 12 | 12° |
| `ithna_ashari` | Ithna Ashari | 16 | 14° |
| `muhammadiyah` | Muhammadiyah | 20 | 18° |

## Tools

| # | Tool | Category | Description |
|---|------|----------|-------------|
| 1 | `get_server_info` | Core | Active config: location, timezone, calculation method, madhab |
| 2 | `list_calculation_methods` | Core | All 10 method IDs with Fajr/Isha angles |
| 3 | `get_prayer_times` | Prayer Times | All 5 prayers + Sunrise for a date and location |
| 4 | `get_next_prayer` | Prayer Times | Name and time of the next upcoming prayer |
| 5 | `get_time_until_next_prayer` | Prayer Times | Minutes until next prayer + human-readable countdown |
| 6 | `get_qibla_direction` | Prayer Times | Bearing in degrees + 16-point cardinal toward Makkah |
| 7 | `get_monthly_prayer_calendar` | Prayer Times | Full month prayer schedule (28–31 days) |
| 8 | `get_sunnah_prayer_times` | Prayer Times | Duha, Awwabin, and Tahajjud time windows |
| 9 | `get_azan_text` | Azan & Iqama | Full Azan text in Arabic and/or transliteration (Fajr variant included) |
| 10 | `get_iqama_time` | Azan & Iqama | Iqama time = adhan + configured offset |
| 11 | `set_iqama_offset` | Azan & Iqama | Update iqama delay (minutes after adhan) per prayer |
| 12 | `get_daily_azan_schedule` | Azan & Iqama | All 5 adhan + iqama times for today |
| 13 | `get_hijri_date` | Islamic Calendar | Today's or a given date's Hijri equivalent |
| 14 | `convert_gregorian_to_hijri` | Islamic Calendar | Gregorian → Hijri conversion |
| 15 | `convert_hijri_to_gregorian` | Islamic Calendar | Hijri → Gregorian conversion |
| 16 | `get_islamic_events` | Islamic Calendar | Named Islamic events for a Hijri year/month with Gregorian dates |
| 17 | `get_ramadan_dates` | Islamic Calendar | Gregorian start and end dates of Ramadan for a given year |
| 18 | `get_eid_dates` | Islamic Calendar | Eid al-Fitr and Eid al-Adha dates for a given year |
| 19 | `get_voluntary_fasting_dates` | Islamic Calendar | Mondays/Thursdays, Ayyam al-Beed, 6 Shawwal, Day of Arafah |
| 20 | `get_morning_adhkar` | Du'a & Dhikr | Complete morning adhkar with Arabic, transliteration, source |
| 21 | `get_evening_adhkar` | Du'a & Dhikr | Complete evening adhkar with Arabic, transliteration, source |
| 22 | `list_dua_topics` | Du'a & Dhikr | All available topic slugs (travel, eating, anxiety, …) |
| 23 | `get_dua_by_topic` | Du'a & Dhikr | All du'as for a given topic |
| 24 | `search_dua` | Du'a & Dhikr | Full-text search across Arabic, transliteration, translation |
| 25 | `get_counter_recommendation` | Du'a & Dhikr | Recommended repetition count and virtues for a dhikr |
| 26 | `get_prayer_dua` | Du'a & Dhikr | Du'as for ruku, sujood, tashahhud, and after salah |
| 27 | `calculate_zakat` | Zakat & Calculators | 2.5% Zakat due on cash, gold, silver, or trade goods above nisab |
| 28 | `calculate_gold_nisab` | Zakat & Calculators | Nisab threshold = 85g × gold price per gram |
| 29 | `calculate_silver_nisab` | Zakat & Calculators | Nisab threshold = 595g × silver price per gram |
| 30 | `calculate_fasting_times` | Zakat & Calculators | Suhoor (Fajr) and Iftar (Maghrib) for a date range (max 31 days) |
| 31 | `calculate_inheritance_basic` | Zakat & Calculators | Faraid fixed shares with Aul handling (Quran 4:11-12) |
| 32 | `get_asma_ul_husna` | 99 Names | All 99 Names of Allah with Arabic, transliteration, and meaning |
| 33 | `get_name_of_allah` | 99 Names | Look up a name by number (1–99) or transliteration |
| 34 | `search_asma_ul_husna` | 99 Names | Search names by meaning, transliteration, or Arabic text |

## Quickstart

```bash
uvx azan-mcp
```

Or with a config file:

```bash
AZAN_CONFIG=/path/to/azan-config.json uvx azan-mcp
```

## Claude Desktop Setup

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "azan": {
      "command": "uvx",
      "args": ["azan-mcp"],
      "env": {
        "AZAN_CONFIG": "/path/to/your/azan-config.json"
      }
    }
  }
}
```

## Configuration

Create an `azan-config.json` file (see `examples/azan-config.example.json`):

```json
{
  "latitude": 21.3891,
  "longitude": 39.8579,
  "timezone": "Asia/Riyadh",
  "calculation_method": "umm_al_qura",
  "madhab": "shafi",
  "iqama_offsets": {
    "fajr": 20, "dhuhr": 10, "asr": 10, "maghrib": 5, "isha": 15
  }
}
```


## Development

```bash
uv sync
uv run pytest tests/ -v --ignore=tests/test_integration.py
```

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 Azan-MCP Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
