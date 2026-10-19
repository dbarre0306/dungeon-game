from typing import Any

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.domain.actors.player.mage import Mage
from dungeon_game.game_state import GameState


class CastHealingNode:
    def __init__(self, dungeon_master_agent: DungeonMasterAgent):
        self._dungeon_master_agent = dungeon_master_agent

    def execute(self, state: GameState) -> dict[str, Any]:
        print("CAST HEALING")
        room = state.get_current_room()
        is_valid, err_msg = room.is_valid_intent(state.intent)
        if not is_valid:
            response = self._dungeon_master_agent.invoke(
                state, err_msg, include_command=True
            )
            return {"narration": [response.narration]}
        player = state.player
        if not isinstance(player, Mage) or player.healing_casts_left <= 0:
            return self._out_of_casts(state)
        return self._cast_healing(state, player)

    def _out_of_casts(self, state: GameState) -> dict[str, Any]:
        narration = self._get_narration(
            state, "The player can't cast the healing spell anymore."
        )
        return self._result(state, narration)

    def _cast_healing(self, state: GameState, player: Mage) -> dict[str, Any]:
        if player.health_points >= player.max_health_points:
            msg = (
                "The player cast the healing spell, but they were already at full "
                "strength, so the spell had no effect and that cast is used up. "
                "You must say that the player was already at full strength. "
                "Do NOT say the spell fizzled or failed."
            )
        else:
            msg = "The player cast the healing spell and is restored to full strength."
        narration = self._get_narration(state, msg)
        return self._result(state, narration, player.with_healed_by_healing_spell())

    def _result(
        self, state: GameState, narration: str, player: Mage | None = None
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "dungeon": state.dungeon.with_room_updated(
                state.player.current_room_index, history=[narration]
            ),
            "narration": [narration],
        }
        if player is not None:
            result["player"] = player
        return result

    def _get_narration(self, state: GameState, msg: str) -> str:
        return self._dungeon_master_agent.invoke(
            state, msg, include_command=True
        ).narration
