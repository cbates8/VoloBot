"""Combat Types"""

from utils.combat.models import Character

ENCOUNTER_TYPE = list[Character]
BINNED_ENCOUNTER_TYPE = dict[int | None, list[Character]]
