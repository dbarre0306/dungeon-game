from typing import Any

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.domain.dice import Dice
from dungeon_game.domain.rooms.combat_room import CombatRoom
from dungeon_game.game_state import GameState
from dungeon_game.nodes.attack import HIT_TARGET


class EnemyAttackNode:
    """The enemy strikes back at the player; the mirror image of `AttackNode`."""

    def __init__(self, dungeon_master_agent: DungeonMasterAgent, dice: Dice | None = None):
        self._dungeon_master_agent = dungeon_master_agent
        self._dice = dice or Dice()

    def execute(self, state: GameState) -> dict[str, Any]:
        print("ENEMY ATTACK")
        room = self._get_combat_room(state)
        if room.enemy.is_dead():
            return {}
        return _EnemyStrike(state, room, self._dungeon_master_agent, self._dice).resolve()

    @staticmethod
    def _get_combat_room(state: GameState) -> CombatRoom:
        room = state.get_current_room()
        if not isinstance(room, CombatRoom):
            raise TypeError("The room must be a CombatRoom")
        return room


class _EnemyStrike:
    """One enemy attack against the player: roll to hit, apply damage, narrate the result."""

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
        player = self._player.take_damage(self._damage())
        if player.is_dead():
            return self._player_dead(player)
        return self._player_wounded(player)

    def _hits(self) -> bool:
        return self._dice.roll(20) + self._enemy.hit_bonus >= HIT_TARGET

    def _damage(self) -> int:
        raw = self._dice.roll(6) + self._enemy.damage_bonus
        return max(1, raw - self._player.get_damage_reduction())

    def _missed(self) -> dict[str, Any]:
        return self._update(
            self._player,
            f"The {self._enemy.name} attacked the player (a {self._player.type}), but missed.",
        )

    def _player_wounded(self, player) -> dict[str, Any]:
        return self._update(
            player,
            f"The {self._enemy.name} attacked the player (a {player.type}) and wounded them."
            f"Describe how the {self._enemy.name} attacked the player "
            f"and how the player was wounded. "
            "Do NOT say anything about the doorway out.",
        )

    def _player_dead(self, player) -> dict[str, Any]:
        return self._update(
            player,
            f"The {self._enemy.name} has killed the player (a {player.type}). "
            "Describe the player's final moments. "
            "Do NOT say anything about what the player should do next.",
        )

    def _update(self, player, msg: str) -> dict[str, Any]:
        narration = self._dungeon_master_agent.invoke(self._room, msg).narration
        return {
            "player": player,
            "dungeon": self._state.dungeon.with_room_updated(
                self._player.current_room_index, history=[narration]
            ),
            "narration": self._state.narration + [narration],
        }
