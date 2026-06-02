from __future__ import annotations

import pytest

import azan_mcp.config as _config_module
from azan_mcp.config import CalculationMethod, Madhab, UserConfig


MAKKAH_CONFIG = UserConfig(
    latitude=21.3891,
    longitude=39.8579,
    timezone="Asia/Riyadh",
    calculation_method=CalculationMethod.UMM_AL_QURA,
    madhab=Madhab.SHAFI,
)

LONDON_CONFIG = UserConfig(
    latitude=51.5074,
    longitude=-0.1278,
    timezone="Europe/London",
    calculation_method=CalculationMethod.MWL,
    madhab=Madhab.SHAFI,
)


@pytest.fixture(autouse=True)
def use_makkah_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_config_module, "_config", MAKKAH_CONFIG)
