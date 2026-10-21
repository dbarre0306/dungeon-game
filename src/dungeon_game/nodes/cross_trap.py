from typing import Any

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.domain.dice import Dice
from dungeon_game.domain.rooms.trap_room import TrapRoom
from dungeon_game.game_state import GameState

# A d20 of at least this strikes the player: 13 in 20 (65%).
TRAP_HIT_TARGET = 8
# On a hit, a d10 of at least this is a major wound; otherwise it is minor.
MAJOR_WOUND_ROLL = 8
MINOR_WOUND_POINTS = 2
MAJOR_WOUND_POINTS = 5
# The gold on the far side is 4 to 6 coins: 3 + a d3.
MIN_GOLD_COINS = 4
GOLD_DIE_SIDES = 3


class CrossTrapNode:
    """The player crosses the trap room: the trap strikes (or misses) and a
    player who survives collects the gold on the far side."""

    def __init__(
        self, dungeon_master_agent: DungeonMasterAgent, dice: Dice | None = None
    ):
        self._dungeon_master_agent = dungeon_master_agent
        self._dice = dice or Dice()

    def execute(self, state: GameState) -> dict[str, Any]:
        print("CROSS TRAP")
        room = state.get_current_room()
        if not isinstance(room, TrapRoom):
            raise TypeError("The room must be a TrapRoom")

        player = state.player
        if self._dice.roll(20) < TRAP_HIT_TARGET:
            gold = self._roll_gold()
            player = player.model_copy(update={"gold_coins": player.gold_coins + gold})
            msg = (
                f"The player (a {player.type}) crossed the room and set off "
                f"the {room.trap_type} trap, but dodged it cleanly. "
                f"On the far side the player collected {gold} gold coins."
            )
        else:
            player, msg = self._on_struck(room, player)
        narration = self._dungeon_master_agent.invoke(
            state.model_copy(update={"player": player}), msg, include_command=True
        ).narration
        return {
            "player": player,
            "dungeon": state.dungeon.with_room_updated(
                player.current_room_index, is_sprung=True, history=[narration]
            ),
            "narration": [narration],
        }

    def _on_struck(self, room: TrapRoom, player):
        is_major = self._dice.roll(10) >= MAJOR_WOUND_ROLL
        severity = "major" if is_major else "minor"
        player = player.with_damage(
            MAJOR_WOUND_POINTS if is_major else MINOR_WOUND_POINTS
        )
        if player.is_dead():
            return player, (
                f"The player (a {player.type}) crossed the room, set off the "
                f"{room.trap_type} trap and suffered a {severity} wound that "
                "killed them. Describe the player's final moments."
            )
        gold = self._roll_gold()
        player = player.model_copy(update={"gold_coins": player.gold_coins + gold})
        return player, (
            f"The player (a {player.type}) crossed the room and set off the "
            f"{room.trap_type} trap. It struck the player with a {severity} "
            f"wound. On the far side the player collected {gold} gold coins."
        )

    def _roll_gold(self) -> int:
        return MIN_GOLD_COINS - 1 + self._dice.roll(GOLD_DIE_SIDES)
