import random
from typing import Any, cast

from dungeon_game.domain.dungeon.dungeon import Dungeon
from dungeon_game.domain.player.player import Player
from dungeon_game.domain.rooms.enemy_room import EnemyRoom
from dungeon_game.game_state import GameState

# Simple d20 "hit" target: roll + to_hit_bonus >= HIT_TARGET means a hit
HIT_TARGET = 12


class AttackNode:

    def __init__(self, dungeon_master_agent):
        self._dungeon_master_agent = dungeon_master_agent

    def execute(self, state: GameState) -> dict[str, Any]:
        print("ATTACK")
        room = state.get_current_room()
        is_valid, err_msg = room.is_valid_action(state.intent)
        if is_valid:
            return self._attack_enemy(state)
        else:
            return {"narration": err_msg}

    def _attack_enemy(self, state: GameState) -> dict[str, Any]:

        dungeon = state.dungeon
        player = state.player
        current_room = state.get_current_room()
        if not isinstance(current_room, EnemyRoom):
            raise TypeError("The room must be an EnemyRoom")
        room = cast(EnemyRoom, current_room)
        enemy = room.enemy

        if self._missed_enemy(state):
            return self._missed_enemy_update(player, room)

        enemy_health_points = enemy.health_points - self._lost_health_points(player)
        if enemy_health_points <= 0:
            return self._enemy_dead_update(dungeon, player, room)

        return self._enemy_wounded_update(
            state.dungeon, player, room, enemy_health_points
        )

    def _lost_health_points(self, player: Player) -> int:
        return self._roll_die(6) + player.get_extra_weapon_damage()

    def _missed_enemy(self, state: GameState) -> bool:
        return not self._hit_enemy(state)

    def _hit_enemy(self, state: GameState) -> bool:
        roll = self._roll_die(20)
        return roll + state.player.hit_bonus >= HIT_TARGET

    def _roll_die(_, num_sides: int) -> int:
        return random.randint(1, num_sides)

    def _missed_enemy_update(self, player: Player, room: EnemyRoom) -> dict[str, Any]:
        return {
            "player": player.model_copy(
                update={
                    "is_fighting": True,
                    "last_action": (
                        f"The player (a {player.type}) attacked the {room.enemy.name} "
                        f"with a {player.get_weapon()}, but missed."
                    ),
                }
            ),
            "narration": "",
        }

    def _enemy_wounded_update(
        self,
        dungeon: Dungeon,
        player: Player,
        room: EnemyRoom,
        enemy_health_points: int,
    ) -> dict[str, Any]:
        return {
            "player": player.model_copy(
                update={
                    "is_fighting": True,
                    "last_action": (
                        f"The player (a {player.type}) attacked the {room.enemy.name} "
                        f"with a {player.get_weapon()} and wounded the {room.enemy.name}."
                    ),
                }
            ),
            "dungeon": dungeon.with_room_updated(
                player.current_room_index,
                enemy=room.enemy.model_copy(
                    update={"health_points": enemy_health_points}
                ),
            ),
            "narration": "",
        }

    def _enemy_dead_update(
        self, dungeon: Dungeon, player: Player, room: EnemyRoom
    ) -> dict[str, Any]:
        return {
            "player": player.model_copy(
                update={
                    "is_fighting": False,
                }
            ),
            "dungeon": dungeon.with_room_updated(
                player.current_room_index,
                events=[f"The {room.enemy.name} was killed (dead)."],
                enemy=room.enemy.model_copy(update={"health_points": 0}),
            ),
            "narration": self._get_narration(player, room),
        }

    def _get_narration(self, player: Player, room: EnemyRoom) -> str:
        msg = {
            "messages": [
                {
                    "role": "user",
                    "content": "Construct a narrative based on the "
                    f"player (a {player.type}) having killed the {room.enemy.name} "
                    f"with a {player.get_weapon()}.  You are speaking to the player. "
                    "Don't go crazy.  Keep it to a couple of sentences at most. "
                    "Do NOT make up any facts such as the sound of dragons or the "
                    "scent of iron. Stick to what it would feel like after a brutal battle. "
                    "Do NOT say anything about what the player should do next.",
                }
            ]
        }

        result = self._dungeon_master_agent.invoke(msg)
        response = result["structured_response"]
        return response.narration
