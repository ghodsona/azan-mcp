from dataclasses import dataclass


@dataclass
class IslamicEvent:
    hijri_month: int
    hijri_day: int
    name: str
    is_public_holiday: bool


ISLAMIC_EVENTS: list[IslamicEvent] = [
    IslamicEvent(1,  1,  "Islamic New Year",               True),
    IslamicEvent(1,  10, "Day of Ashura",                  False),
    IslamicEvent(3,  12, "Mawlid al-Nabi",                 True),
    IslamicEvent(7,  27, "Isra and Mi'raj",                True),
    IslamicEvent(8,  15, "Laylat al-Bara'ah",              False),
    IslamicEvent(9,  1,  "Start of Ramadan",               True),
    IslamicEvent(9,  27, "Laylat al-Qadr (likely)",        False),
    IslamicEvent(10, 1,  "Eid al-Fitr",                    True),
    IslamicEvent(12, 8,  "Hajj begins (Yawm al-Tarwiyah)", False),
    IslamicEvent(12, 9,  "Day of Arafah",                  False),
    IslamicEvent(12, 10, "Eid al-Adha",                    True),
]
