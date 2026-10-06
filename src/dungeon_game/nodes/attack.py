from typing import Any

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.domain.dice import Dice
from dungeon_game.domain.rooms.combat_room import CombatRoom
from dungeon_game.game_state import GameState

# Simple d20 "hit" target: roll + to_hit_bonus >= HIT_TARGET means a hit
HIT_TARGET = 12


class AttackNode:
    """The player strikes at the enemy; `EnemyAttackNode` is its mirror image."""

    def __init__(self, dungeon_master_agent: DungeonMasterAgent, dice: Dice | None = None):
        self._dungeon_master_agent = dungeon_master_agent
        self._dice = dice or Dice()

    def execute(self, state: GameState) -> dict[str, Any]:
        print("ATTACK")
        room = state.get_current_room()
        is_valid, err_msg = room.is_valid_action(state.intent)
        if not is_valid:
            return {"narration": [err_msg]}
        return _PlayerStrike(
            state, self._get_combat_room(state), self._dungeon_master_agent, self._dice
        ).resolve()

    @staticmethod
    def _get_combat_room(state: GameState) -> CombatRoom:
        room = state.get_current_room()
        if not isinstance(room, CombatRoom):
            raise TypeError("The room must be a CombatRoom")
        return room


class _PlayerStrike:
    """One player attack against the enemy: roll to hit, apply damage, narrate the result."""

    def __init__(
        self,
        state: GameState,
        room: CombatRoom,
        dungeon_master_agent: DungeonMasterAgent,
        dice: Dice,
    ):
        self._state = state
        self._player = state.player
        self._room = room
        self._enemy = room.enemy
        self._dungeon_master_agent = dungeon_master_agent
        self._dice = dice

    def resolve(self) -> dict[str, Any]:
        if not self._hits():
            return self._missed()
        enemy_health_points = self._enemy.health_points - self._damage()
        if enemy_health_points <= 0:
            return self._enemy_dead()
        return self._enemy_wounded(enemy_health_points)

    def _hits(self) -> bool:
        return self._dice.roll(20) + self._player.hit_bonus >= HIT_TARGET

    def _damage(self) -> int:
        return self._dice.roll(6) + self._player.get_extra_weapon_damage()

    def _missed(self) -> dict[str, Any]:
        return self._update(
            True,
            f"The player (a {self._player.type}) attacked the {self._enemy.name} "
            f"with a {self._player.get_weapon()}, but missed."
            "Ignore the gold coins; stay focused on the battle. "
            "Do NOT say anything about the doorway out.",
        )

    def _enemy_wounded(self, enemy_health_points: int) -> dict[str, Any]:
        return self._update(
            True,
            f"The player (a {self._player.type}) attacked the {self._enemy.name} "
            f"with a {self._player.get_weapon()}.  The {self._enemy.name} was wounded."
            f"Describe how the player attacked the {self._enemy.name} "
            f"and how the {self._enemy.name} was wounded. "
            "Ignore the gold coins; stay focused on the battle. "
            "Do NOT say anything about the doorway out.",
            enemy=self._enemy.model_copy(update={"health_points": enemy_health_points}),
        )

    def _enemy_dead(self) -> dict[str, Any]:
        return self._update(
            False,
            f"The player (a {self._player.type}) has killed the {self._enemy.name} "
            f"with a {self._player.get_weapon()}.  "
            "Stick to what it would feel like after a brutal battle. "
            "Do NOT say anything about what the player should do next.",
            enemy=self._enemy.model_copy(update={"health_points": 0}),
        )

    def _update(self, is_fighting: bool, msg: str, **room_updates: Any) -> dict[str, Any]:
        narration = self._dungeon_master_agent.invoke(self._room, msg).narration
        return {
            "player": self._player.model_copy(update={"is_fighting": is_fighting}),
            "dungeon": self._state.dungeon.with_room_updated(
                self._player.current_room_index, history=[narration], **room_updates
            ),
            "narration": [narration],
        }
