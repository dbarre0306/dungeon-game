from typing import Any, cast

from dungeon_game.domain.rooms.dungeon_room import DungeonRoom
from dungeon_game.domain.rooms.enemy_room import EnemyRoom
from dungeon_game.game_state import GameState


class AttackNode:

    def execute(self, state: GameState) -> dict[str, Any]:
        room = self._get_room(state)
        is_valid, err_msg = room.is_valid_action(state.action)
        if is_valid:
            return self._attack_enemy(state)
        else:
            # we need to go to the next node (counterattack)
            return {"narration": err_msg}

    def _attack_enemy(self, state: GameState) -> dict[str, Any]:
        pass

    def _get_room(self, state: GameState) -> DungeonRoom:
        return state.dungeon.get_room(state.player.current_room_index)
