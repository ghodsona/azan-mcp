from __future__ import annotations

import json
from pathlib import Path

_DATA_DIR = Path(__file__).parent

_adhkar_cache: list[dict] | None = None
_duas_cache: list[dict] | None = None
_asma_cache: list[dict] | None = None


def load_adhkar() -> list[dict]:
    global _adhkar_cache
    if _adhkar_cache is None:
        _adhkar_cache = json.loads((_DATA_DIR / "adhkar.json").read_text(encoding="utf-8"))
    return _adhkar_cache


def load_duas() -> list[dict]:
    global _duas_cache
    if _duas_cache is None:
        _duas_cache = json.loads((_DATA_DIR / "duas.json").read_text(encoding="utf-8"))
    return _duas_cache


def load_asma_ul_husna() -> list[dict]:
    global _asma_cache
    if _asma_cache is None:
        _asma_cache = json.loads((_DATA_DIR / "asma_ul_husna.json").read_text(encoding="utf-8"))
    return _asma_cache
