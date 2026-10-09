from typing import Any

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.domain.actors.player.player import Player
from dungeon_game.domain.dungeon.dungeon import Dungeon
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom
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
            return {"narration": [err_msg]}

    def _drink_potion(self, state: GameState) -> dict[str, Any]:
        player = state.player
        if player.potions.quantity <= 0:
            return self._out_of_potions(state)
        return self._drink_one_potion(state.dungeon, player, state.get_current_room())

    def _out_of_potions(self, state: GameState) -> dict[str, Any]:
        narration = self._get_narration(
            state.get_current_room(),
            state.player,
            "You don't have anymore potions to drink.",
        )
        return {
            "dungeon": state.dungeon.with_room_updated(
                state.player.current_room_index,
                history=[narration],
            ),
            "narration": [narration],
        }

    def _drink_one_potion(
        self, dungeon: Dungeon, player: Player, room: DungeonRoom
    ) -> dict[str, Any]:
        new_quantity = player.potions.quantity - 1
        new_health_points = min(
            player.max_health_points,
            player.health_points + player.potions.health_points,
        )

        if player.health_points >= player.max_health_points:
            return self._potion_did_not_help(dungeon, player, room, new_quantity)
        return self._potion_helped(
            dungeon, player, room, new_quantity, new_health_points
        )

    def _potion_did_not_help(
        self, dungeon: Dungeon, player: Player, room: DungeonRoom, new_quantity: int
    ) -> dict[str, Any]:
        narration = self._get_narration(
            room, player, "The player drank a potion but gained no extra strength."
        )
        return {
            "player": player.model_copy(
                update={
                    "potions": player.potions.model_copy(
                        update={"quantity": new_quantity}
                    ),
                }
            ),
            "dungeon": dungeon.with_room_updated(
                player.current_room_index,
                history=[narration],
            ),
            "narration": [narration],
        }

    def _potion_helped(
        self,
        dungeon: Dungeon,
        player: Player,
        room: DungeonRoom,
        new_quantity: int,
        new_health_points: int,
    ) -> dict[str, Any]:
        narration = self._get_narration(
            room, player, "The player gained strength by drinking the potion."
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
            "dungeon": dungeon.with_room_updated(
                player.current_room_index,
                history=[narration],
            ),
            "narration": [narration],
        }

    def _get_narration(self, room: DungeonRoom, player: Player, msg: str) -> str:
        return self._dungeon_master_agent.invoke(room, player, msg).narration
