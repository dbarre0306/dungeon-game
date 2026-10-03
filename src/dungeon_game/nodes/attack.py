import random
from typing import Any, cast

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.domain.dungeon.dungeon import Dungeon
from dungeon_game.domain.npc.enemy import Enemy
from dungeon_game.domain.player.player import Player
from dungeon_game.domain.rooms.combat_room import CombatRoom
from dungeon_game.domain.rooms.dungeon_room import DungeonRoom
from dungeon_game.domain.rooms.monster_room import MonsterRoom
from dungeon_game.game_state import GameState

# Simple d20 "hit" target: roll + to_hit_bonus >= HIT_TARGET means a hit
HIT_TARGET = 12


class AttackNode:
    def __init__(self, dungeon_master_agent: DungeonMasterAgent):
        self._dungeon_master_agent = dungeon_master_agent

    def execute(self, state: GameState) -> dict[str, Any]:
        print("ATTACK")
        room = state.get_current_room()
        is_valid, err_msg = room.is_valid_action(state.intent)
        if is_valid:
            return self._attack_enemy(state)
        else:
            return {"narration": [err_msg]}

    def _attack_enemy(self, state: GameState) -> dict[str, Any]:

        dungeon = state.dungeon
        player = state.player
        room = self._get_combat_room(state)

        if self._missed_enemy(state):
            return self._missed_enemy_update(dungeon, player, room)

        enemy_health_points = room.enemy.health_points - self._lost_health_points(
            player
        )
        if enemy_health_points <= 0:
            return self._enemy_dead_update(dungeon, player, room)

        return self._enemy_wounded_update(
            state.dungeon, player, room, enemy_health_points
        )

    def _get_combat_room(self, state: GameState) -> CombatRoom:
        current_room = state.get_current_room()
        if not isinstance(current_room, CombatRoom):
            raise TypeError("The room must be an CombatRoom")
        return cast(CombatRoom, current_room)

    def _lost_health_points(self, player: Player) -> int:
        return self._roll_die(6) + player.get_extra_weapon_damage()

    def _missed_enemy(self, state: GameState) -> bool:
        return not self._hit_enemy(state)

    def _hit_enemy(self, state: GameState) -> bool:
        roll = self._roll_die(20)
        return roll + state.player.hit_bonus >= HIT_TARGET

    def _roll_die(_, num_sides: int) -> int:
        return random.randint(1, num_sides)

    def _missed_enemy_update(
        self, dungeon: Dungeon, player: Player, room: CombatRoom
    ) -> dict[str, Any]:
        narration = self._missed_enemy_narration(player, room)
        return {
            "player": player.model_copy(
                update={
                    "is_fighting": True,
                }
            ),
            "dungeon": dungeon.with_room_updated(
                player.current_room_index,
                narration=[narration],
            ),
            "narration": [narration],
        }

    def _missed_enemy_narration(self, player: Player, room: CombatRoom) -> str:
        msg = (
            f"The player (a {player.type}) attacked the {room.enemy.name} "
            f"with a {player.get_weapon()}, but missed."
        )

        return self._dungeon_master_agent.invoke(room, msg).narration

    def _enemy_wounded_update(
        self,
        dungeon: Dungeon,
        player: Player,
        room: CombatRoom,
        enemy_health_points: int,
    ) -> dict[str, Any]:

        narration = self._enemy_wounded_narration(player, room)
        return {
            "player": player.model_copy(
                update={
                    "is_fighting": True,
                }
            ),
            "dungeon": dungeon.with_room_updated(
                player.current_room_index,
                enemy=room.enemy.model_copy(
                    update={"health_points": enemy_health_points}
                ),
                narration=[narration],
            ),
            "narration": [narration],
        }

    def _enemy_wounded_narration(self, player: Player, room: CombatRoom) -> str:
        msg = (
            f"The player (a {player.type}) attacked the {room.enemy.name} "
            f"with a {player.get_weapon()}.  The {room.enemy.name} was wounded."
        )

        return self._dungeon_master_agent.invoke(room, msg).narration

    def _enemy_dead_update(
        self, dungeon: Dungeon, player: Player, room: CombatRoom
    ) -> dict[str, Any]:

        narration = self._enemy_dead_narration(player, room)
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
                narration=[narration],
            ),
            "narration": [narration],
        }

    def _enemy_dead_narration(self, player: Player, room: CombatRoom) -> str:
        msg = (
            f"The player (a {player.type}) has killed the {room.enemy.name} "
            f"with a {player.get_weapon()}.  "
            "Stick to what it would feel like after a brutal battle. "
            "Do NOT say anything about what the player should do next."
        )

        return self._dungeon_master_agent.invoke(room, msg).narration
