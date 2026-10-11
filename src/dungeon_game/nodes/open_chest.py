from typing import Any

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.domain.dice import Dice
from dungeon_game.domain.rooms.treasure_room import TreasureRoom
from dungeon_game.game_state import GameState

# The gold in the chest is 3 to 6 coins: 2 + a d4.
MIN_GOLD_COINS = 3
GOLD_DIE_SIDES = 4


class OpenChestNode:
    """The player opens a chest: gold is collected at once, while a serpent
    attacks the player, who is then fighting until it is dead."""

    def __init__(
        self, dungeon_master_agent: DungeonMasterAgent, dice: Dice | None = None
    ):
        self._dungeon_master_agent = dungeon_master_agent
        self._dice = dice or Dice()

    def execute(self, state: GameState) -> dict[str, Any]:
        print(f"OPEN CHEST : {state.intent.chest_side}")
        room = state.get_current_room()
        is_valid, msg = room.is_valid_intent(state.intent)
        if not is_valid:
            response = self._dungeon_master_agent.invoke(room, state.player, msg)
            return {"narration": [response.narration]}
        if not isinstance(room, TreasureRoom):
            raise TypeError("The room must be a TreasureRoom")
        side = state.intent.chest_side
        if side == room.serpent_side:
            return self._release_serpent(state, room)
        return self._collect_gold(state, room)

    def _release_serpent(self, state: GameState, room: TreasureRoom) -> dict[str, Any]:
        player = state.player.model_copy(update={"is_fighting": True})
        room = room.model_copy(update={"opened_side": state.intent.chest_side})
        narration = self._dungeon_master_agent.invoke(
            room,
            player,
            f"The player (a {player.type}) opened the {room.opened_side} chest "
            "and a serpent lunged out of it. Do NOT say that the serpent bit "
            "or wounded the player. You must tell the player that they must "
            "kill the serpent.",
        ).narration
        return self._update(state, player, narration)

    def _collect_gold(self, state: GameState, room: TreasureRoom) -> dict[str, Any]:
        gold = MIN_GOLD_COINS - 1 + self._dice.roll(GOLD_DIE_SIDES)
        player = state.player.model_copy(
            update={"gold_coins": state.player.gold_coins + gold}
        )
        room = room.model_copy(update={"opened_side": state.intent.chest_side})
        narration = self._dungeon_master_agent.invoke(
            room,
            player,
            f"The player (a {player.type}) opened the {room.opened_side} chest "
            f"and collected {gold} gold coins.",
        ).narration
        return self._update(state, player, narration)

    @staticmethod
    def _update(state: GameState, player, narration: str) -> dict[str, Any]:
        return {
            "player": player,
            "dungeon": state.dungeon.with_room_updated(
                player.current_room_index,
                opened_side=state.intent.chest_side,
                history=[narration],
            ),
            "narration": [narration],
        }
