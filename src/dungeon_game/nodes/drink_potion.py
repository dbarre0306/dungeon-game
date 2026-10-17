from typing import Any

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.game_state import GameState


class DrinkPotionNode:
    def __init__(self, dungeon_master_agent: DungeonMasterAgent):
        self._dungeon_master_agent = dungeon_master_agent

    def execute(self, state: GameState) -> dict[str, Any]:
        print("DRINK POTION")
        room = state.get_current_room()
        is_valid, err_msg = room.is_valid_intent(state.intent)
        if is_valid:
            return self._drink_potion(state)
        else:
            response = self._dungeon_master_agent.invoke(
                state, err_msg, include_command=True
            )
            return {"narration": [response.narration]}

    def _drink_potion(self, state: GameState) -> dict[str, Any]:
        player = state.player
        if player.potions.quantity <= 0:
            return self._out_of_potions(state)
        return self._drink_one_potion(state)

    def _out_of_potions(self, state: GameState) -> dict[str, Any]:
        narration = self._get_narration(
            state, "You don't have anymore potions to drink."
        )
        return {
            "dungeon": state.dungeon.with_room_updated(
                state.player.current_room_index,
                history=[narration],
            ),
            "narration": [narration],
        }

    def _drink_one_potion(self, state: GameState) -> dict[str, Any]:
        player = state.player
        new_quantity = player.potions.quantity - 1
        new_health_points = min(
            player.max_health_points,
            player.health_points + player.potions.health_points,
        )

        if player.health_points >= player.max_health_points:
            return self._potion_did_not_help(state, new_quantity)
        return self._potion_helped(state, new_quantity, new_health_points)

    def _potion_did_not_help(
        self, state: GameState, new_quantity: int
    ) -> dict[str, Any]:
        player = state.player
        narration = self._get_narration(
            state, "The player drank a potion but gained no extra strength."
        )
        return {
            "player": player.model_copy(
                update={
                    "potions": player.potions.model_copy(
                        update={"quantity": new_quantity}
                    ),
                }
            ),
            "dungeon": state.dungeon.with_room_updated(
                player.current_room_index,
                history=[narration],
            ),
            "narration": [narration],
        }

    def _potion_helped(
        self,
        state: GameState,
        new_quantity: int,
        new_health_points: int,
    ) -> dict[str, Any]:
        player = state.player
        narration = self._get_narration(
            state, "The player gained strength by drinking the potion."
        )
        return {
            "player": player.model_copy(
                update={
                    "health_points": new_health_points,
                    "potions": player.potions.model_copy(
                        update={"quantity": new_quantity}
                    ),
                }
            ),
            "dungeon": state.dungeon.with_room_updated(
                player.current_room_index,
                history=[narration],
            ),
            "narration": [narration],
        }

    def _get_narration(self, state: GameState, msg: str) -> str:
        return self._dungeon_master_agent.invoke(
            state, msg, include_command=True
        ).narration
