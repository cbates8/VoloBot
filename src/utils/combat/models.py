"""Combat object Pydantic models"""

from pydantic import BaseModel
from typing import Literal


class HitPoints(BaseModel):
    """Model representing character hit points"""

    current: int
    max: int | None = None
    temp: int | None = None
    hint: str | None = None


class Condition(BaseModel):
    """Model representing character conditions"""

    name: str | None = None
    duration: str | None = None


class Character(BaseModel):
    """Model representing a character"""

    name: str
    type: Literal["pc", "npc"]
    initiative: int | None = None
    hp: HitPoints | None = None
    ac: int | None = None
    conditions: list[Condition] | None = None
