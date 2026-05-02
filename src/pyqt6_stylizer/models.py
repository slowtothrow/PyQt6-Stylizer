from __future__ import annotations

from enum import Enum


class ExperienceLevel(str, Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

    @property
    def label(self) -> str:
        return self.value.capitalize()

    def supports(self, minimum_level: "ExperienceLevel") -> bool:
        ordered = self.ordered()
        return ordered.index(self) >= ordered.index(minimum_level)

    @classmethod
    def from_value(cls, value: str | None) -> "ExperienceLevel":
        if value is None:
            return cls.BASIC

        for member in cls:
            if member.value == value:
                return member
        return cls.BASIC

    @classmethod
    def ordered(cls) -> tuple["ExperienceLevel", ...]:
        return (cls.BASIC, cls.INTERMEDIATE, cls.ADVANCED)
