"""Copy and class data shown on the home page (sourced from APP.md)."""

from dataclasses import dataclass

TITLE = "Dungeon of Mistwood"
QUEST = (
    "A troll has stolen the Amulet of Valdorin. Fight through the dungeon, "
    "face the troll on its throne, and retrieve the amulet."
)

ABOUT = (
    "Mistwood is a text adventure. A narrator describes where you are, you type "
    "what your character does in plain English, and the dice decide how it goes. "
    "No board, no rules to memorize. Each game takes about 5 to 15 minutes, and "
    "no two games visit the same rooms in the same order."
)

HOW_TO_PLAY = [
    "Choose your hero below, a Warrior or a Mage, and press its play button.",
    "Read the scene the narrator describes.",
    "Type one action in plain English, such as “Attack the goblin”, "
    "“Buy a bottle of potion” or “Go into the left passageway”.",
    "The game rolls the dice and the narrator tells you what happened. "
    "Your Health Points (HP), items and gold coins update to match.",
    "The gold coins can be used to purchase items of value from a merchant.",
    "You must defeat the troll to win. "
    "If your Health Points (HP) reach zero, you are dead and have failed in "
    "your quest.",
]


@dataclass(frozen=True)
class PlayerClass:
    key: str
    name: str
    tagline: str
    stats: list[tuple[str, str]]


WARRIOR = PlayerClass(
    key="warrior",
    name="Warrior",
    tagline="Hard to hit and steady in a long fight.",
    stats=[
        ("Health", "25 Health Points (HP)"),
        ("Gear", "Sword and shield"),
        ("Special", "The shield provides protection, but can be damaged or broken"),
        ("Starts with", "10 gold coins, 2 bottles of potion"),
    ],
)

MAGE = PlayerClass(
    key="mage",
    name="Mage",
    tagline="Fragile, but a firebolt hits hard.",
    stats=[
        ("Health", "18 Health Points (HP)"),
        ("Gear", "Staff"),
        ("Special", "Cast spells to throw fire bolts or to fully heal thyself"),
        ("Starts with", "10 gold coins"),
    ],
)

CLASSES = [WARRIOR, MAGE]
