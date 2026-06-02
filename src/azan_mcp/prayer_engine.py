"""
Prayer time calculation engine — Meeus solar algorithm (stdlib only).

Based on "Astronomical Algorithms" by Jean Meeus (2nd ed.) and the
adhan-js reference implementation (batoulapps/adhan-js).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


# ---------------------------------------------------------------------------
# Calculation method parameters
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MethodParams:
    fajr_angle: float
    isha_angle: float | None = None
    isha_minutes: int | None = None          # interval after Maghrib
    isha_minutes_ramadan: int | None = None  # interval after Maghrib during Ramadan


METHOD_PARAMS: dict[str, MethodParams] = {
    "umm_al_qura":  MethodParams(fajr_angle=18.5, isha_minutes=90, isha_minutes_ramadan=120),
    "muhammadiyah": MethodParams(fajr_angle=20.0, isha_angle=18.0),
    "mwl":          MethodParams(fajr_angle=18.0, isha_angle=17.0),
    "egypt":        MethodParams(fajr_angle=19.5, isha_angle=17.5),
    "karachi":      MethodParams(fajr_angle=18.0, isha_angle=18.0),
    "isna":         MethodParams(fajr_angle=15.0, isha_angle=15.0),
    "ithna_ashari": MethodParams(fajr_angle=16.0, isha_angle=14.0),
    "tehran":       MethodParams(fajr_angle=17.7, isha_angle=14.0),
    "uoif":         MethodParams(fajr_angle=12.0, isha_angle=12.0),
    "kuwait":       MethodParams(fajr_angle=18.0, isha_angle=17.5),
}

KAABA_LAT = 21.4225
KAABA_LNG = 39.8262


# ---------------------------------------------------------------------------
# Polar-day / polar-night error types
# ---------------------------------------------------------------------------

class PolarDayError(ValueError):
    pass


class PolarNightError(ValueError):
    pass


# ---------------------------------------------------------------------------
# Helper: degrees ↔ radians
# ---------------------------------------------------------------------------

def _rad(deg: float) -> float:
    return math.radians(deg)


def _deg(rad: float) -> float:
    return math.degrees(rad)


def _norm360(x: float) -> float:
    return x % 360.0


# ---------------------------------------------------------------------------
# Meeus solar algorithm
# ---------------------------------------------------------------------------

def julian_day(year: int, month: int, day: int, hour: float = 12.0) -> float:
    """Julian Day Number for a given UT date/time."""
    if month <= 2:
        year -= 1
        month += 12
    A = int(year / 100)
    B = 2 - A + int(A / 4)
    return int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + hour / 24.0 + B - 1524.5


def julian_century(jd: float) -> float:
    return (jd - 2451545.0) / 36525.0


def mean_solar_longitude(T: float) -> float:
    """Mean longitude of the Sun in degrees (Meeus eq. 27.2)."""
    return _norm360(280.46646 + 36000.76983 * T + 0.0003032 * T * T)


def mean_anomaly(T: float) -> float:
    """Mean anomaly of the Sun in degrees (Meeus eq. 27.3)."""
    return _norm360(357.52911 + 35999.05029 * T - 0.0001537 * T * T)


def equation_of_center(T: float) -> float:
    """Sun's equation of the center in degrees."""
    M = _rad(mean_anomaly(T))
    return (
        (1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(M)
        + (0.019993 - 0.000101 * T) * math.sin(2 * M)
        + 0.000289 * math.sin(3 * M)
    )


def sun_true_longitude(T: float) -> float:
    return mean_solar_longitude(T) + equation_of_center(T)


def sun_apparent_longitude(T: float) -> float:
    """Sun's apparent longitude (corrected for aberration and nutation)."""
    omega = 125.04 - 1934.136 * T
    return sun_true_longitude(T) - 0.00569 - 0.00478 * math.sin(_rad(omega))


def mean_obliquity_ecliptic(T: float) -> float:
    """Mean obliquity of the ecliptic in degrees (Meeus eq. 22.2)."""
    return (
        23.0
        + 26.0 / 60.0
        + 21.448 / 3600.0
        - (46.8150 / 3600.0) * T
        - (0.00059 / 3600.0) * T * T
        + (0.001813 / 3600.0) * T * T * T
    )


def apparent_obliquity(T: float) -> float:
    """Apparent obliquity corrected for nutation."""
    omega = 125.04 - 1934.136 * T
    return mean_obliquity_ecliptic(T) + 0.00256 * math.cos(_rad(omega))


def solar_declination(T: float) -> float:
    """Sun's declination in degrees."""
    eps = apparent_obliquity(T)
    lam = sun_apparent_longitude(T)
    return _deg(math.asin(math.sin(_rad(eps)) * math.sin(_rad(lam))))


def equation_of_time(T: float) -> float:
    """Equation of time in minutes (Meeus ch. 27)."""
    eps = _rad(apparent_obliquity(T))
    L0  = _rad(mean_solar_longitude(T))
    e   = 0.016708634 - 0.000042037 * T - 0.0000001267 * T * T
    M   = _rad(mean_anomaly(T))
    y   = math.tan(eps / 2) ** 2
    return _deg(
        y * math.sin(2 * L0)
        - 2 * e * math.sin(M)
        + 4 * e * y * math.sin(M) * math.cos(2 * L0)
        - 0.5 * y * y * math.sin(4 * L0)
        - 1.25 * e * e * math.sin(2 * M)
    ) * 4.0  # convert degrees → minutes


def solar_noon_utc_minutes(lng: float, T: float) -> float:
    """Solar noon in minutes past UTC midnight."""
    return 720.0 - 4.0 * lng - equation_of_time(T)


def hour_angle(lat: float, decl: float, angle: float) -> float:
    """
    Hour angle in degrees for a given depression/elevation angle.

    Raises PolarDayError if the sun never sets (angle never reached going down).
    Raises PolarNightError if the sun never rises (angle never reached going up).
    """
    cos_ha = (
        math.cos(_rad(90.0 + angle))
        - math.sin(_rad(lat)) * math.sin(_rad(decl))
    ) / (math.cos(_rad(lat)) * math.cos(_rad(decl)))

    if cos_ha < -1.0:
        raise PolarDayError(f"Sun never reaches angle {angle}° below horizon at lat={lat:.2f}°")
    if cos_ha > 1.0:
        raise PolarNightError(f"Sun never reaches angle {angle}° above horizon at lat={lat:.2f}°")
    return _deg(math.acos(cos_ha))


def asr_hour_angle(lat: float, decl: float, madhab: str) -> float:
    """Hour angle for Asr based on madhab shadow ratio."""
    shadow_ratio = 2.0 if madhab == "hanafi" else 1.0
    target_angle = _deg(math.atan(1.0 / (shadow_ratio + math.tan(abs(_rad(lat - decl))))))
    return hour_angle(lat, decl, -target_angle)


def _minutes_to_datetime(utc_minutes: float, ref_date: date, tz: ZoneInfo) -> datetime:
    """Convert UTC-minutes-past-midnight into a timezone-aware datetime."""
    utc_midnight = datetime(ref_date.year, ref_date.month, ref_date.day,
                            tzinfo=ZoneInfo("UTC"))
    return (utc_midnight + timedelta(minutes=utc_minutes)).astimezone(tz)


# ---------------------------------------------------------------------------
# Ramadan detection (for Umm al-Qura variable Isha)
# ---------------------------------------------------------------------------

def _is_ramadan(d: date) -> bool:
    from hijridate import Gregorian  
    h = Gregorian(d.year, d.month, d.day).to_hijri()
    return h.month == 9


# ---------------------------------------------------------------------------
# Main computation
# ---------------------------------------------------------------------------

def compute_prayer_times(
    lat: float,
    lng: float,
    date_: date,
    method: str,
    madhab: str,
    timezone: str,
) -> dict[str, datetime]:
    """
    Compute the five daily prayer times plus Sunrise.

    Returns a dict with keys: fajr, sunrise, dhuhr, asr, maghrib, isha.
    All values are timezone-aware datetimes.

    Raises PolarDayError or PolarNightError for extreme latitudes where
    certain prayer times cannot be determined.
    """
    if method not in METHOD_PARAMS:
        raise ValueError(
            f"Unknown calculation method: {method!r}. "
            f"Valid: {', '.join(METHOD_PARAMS)}"
        )

    params = METHOD_PARAMS[method]
    tz = ZoneInfo(timezone)

    # Julian century at solar noon for this date
    jd = julian_day(date_.year, date_.month, date_.day)
    T  = julian_century(jd)

    decl    = solar_declination(T)
    noon_ut = solar_noon_utc_minutes(lng, T)

    # Sunrise / Maghrib: standard 0.833° depression (refraction + solar disc)
    ha_sun   = hour_angle(lat, decl, 0.833)
    ha_fajr  = hour_angle(lat, decl, params.fajr_angle)
    ha_asr   = asr_hour_angle(lat, decl, madhab)

    sunrise_ut  = noon_ut - ha_sun   * 4.0
    maghrib_ut  = noon_ut + ha_sun   * 4.0
    fajr_ut     = noon_ut - ha_fajr  * 4.0
    dhuhr_ut    = noon_ut + 1.0      # 1 min after solar noon (safety margin)
    asr_ut      = noon_ut + ha_asr   * 4.0

    # Isha
    if params.isha_angle is not None:
        ha_isha = hour_angle(lat, decl, params.isha_angle)
        isha_ut = noon_ut + ha_isha * 4.0
    else:
        # Interval-based (Umm al-Qura)
        minutes = (
            params.isha_minutes_ramadan
            if (params.isha_minutes_ramadan and _is_ramadan(date_))
            else params.isha_minutes
        )
        isha_ut = maghrib_ut + (minutes or 90)

    return {
        "fajr":    _minutes_to_datetime(fajr_ut,    date_, tz),
        "sunrise": _minutes_to_datetime(sunrise_ut, date_, tz),
        "dhuhr":   _minutes_to_datetime(dhuhr_ut,   date_, tz),
        "asr":     _minutes_to_datetime(asr_ut,     date_, tz),
        "maghrib": _minutes_to_datetime(maghrib_ut, date_, tz),
        "isha":    _minutes_to_datetime(isha_ut,    date_, tz),
    }


# ---------------------------------------------------------------------------
# Qibla bearing
# ---------------------------------------------------------------------------

def qibla_bearing(lat: float, lng: float) -> float:
    """Great-circle bearing in degrees (0–360) from given location toward the Kaaba."""
    lat1 = _rad(lat)
    lat2 = _rad(KAABA_LAT)
    delta_lng = _rad(KAABA_LNG - lng)
    x = math.sin(delta_lng) * math.cos(lat2)
    y = (math.cos(lat1) * math.sin(lat2)
         - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lng))
    return (_deg(math.atan2(x, y)) + 360.0) % 360.0


def bearing_to_cardinal(bearing: float) -> str:
    """Convert a bearing (0–360°) to a 16-point compass label."""
    points = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW",
    ]
    idx = round(bearing / 22.5) % 16
    return points[idx]
