from typing import Any

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.domain.player.player import Player
from dungeon_game.game_state import GameState


class DrinkPotionNode:

    def __init__(self, dungeon_master_agent: DungeonMasterAgent):
        self._dungeon_master_agent = dungeon_master_agent

    def execute(self, state: GameState) -> dict[str, Any]:
        print("DRINK POTION")
        room = state.get_current_room()
        is_valid, err_msg = room.is_valid_action(state.intent)
        if is_valid:
            return self._drink_potion(state)
        else:
            return {"narration": err_msg}

    def _drink_potion(self, state: GameState) -> dict[str, Any]:
        player = state.player
        if player.potions.quantity <= 0:
            return self._out_of_potions(state)
        return self._drink_one_potion(player)

    def _out_of_potions(self, state: GameState) -> dict[str, Any]:
        return {
            "player": state.player.model_copy(
                update={
                    "last_action": (
                        f"The player tried to drink a potion "
                        "but didn't have any potions left to drink."
                    ),
                }
            ),
            "narration": self._get_narration(
                "You don't have anymore potions to drink."
            ),
        }

    def _drink_one_potion(self, player: Player) -> dict[str, Any]:
        print(f"Current health points: {player.health_points}")
        new_quantity = player.potions.quantity - 1
        new_health_points = min(
            player.max_health_points,
            player.health_points + player.potions.health_points,
        )

        print(f"Max health points: {player.max_health_points}")
        print(f"New health points: {new_health_points}")
        print(f"Potion health points: {player.potions.health_points}")
        if player.health_points >= player.max_health_points:
            return self._potion_did_not_help(player, new_quantity)
        return self._potion_helped(player, new_quantity, new_health_points)

    def _potion_did_not_help(self, player: Player, new_quantity: int) -> dict[str, Any]:
        return {
            "player": player.model_copy(
                update={
                    "potions": player.potions.model_copy(
                        update={"quantity": new_quantity}
                    ),
                    "last_action": (
                        "The player drank a potion but gained no extra strength."
                    ),
                }
            ),
            "narration": self._get_narration(
                "The player drank a potion but gained no extra strength."
            ),
        }

    def _potion_helped(
        self, player: Player, new_quantity: int, new_health_points: int
    ) -> dict[str, Any]:
        return {
            "player": player.model_copy(
                update={
                    "health_points": new_health_points,
                    "potions": player.potions.model_copy(
                        update={"quantity": new_quantity}
                    ),
                    "last_action": ("The player drank a potion gained strength."),
                }
            ),
            "narration": self._get_narration(
                "The player gained strength by drinking the potion."
            ),
        }

    def _get_narration(self, msg: str) -> str:
        return self._dungeon_master_agent.invoke(msg).narration
