from typing import Any

from dungeon_game.domain.actors.player.player import Player
from dungeon_game.domain.rooms.combat_room import CombatRoom
from dungeon_game.game_state import GameState
from dungeon_game.nodes.attack import HIT_TARGET, AttackNode, _Strike


class EnemyAttackNode(AttackNode):
    """The enemy strikes back at the player; the mirror image of `PlayerAttackNode`."""

    _label = "ENEMY ATTACK"

    def _early_result(self, state: GameState) -> dict[str, Any] | None:
        if self._get_combat_room(state).enemy.is_dead():
            return {}
        return None

    def _new_strike(self, state: GameState, room: CombatRoom) -> "_EnemyStrike":
        return _EnemyStrike(state, room, self._dungeon_master_agent, self._dice)


class _EnemyStrike(_Strike[Player]):
    """One enemy attack against the player."""

    def _hits(self) -> bool:
        return self._dice.roll(20) + self._enemy.hit_bonus >= HIT_TARGET

    def _damage(self) -> int:
        raw = self._dice.roll(6) + self._enemy.get_extra_damage()
        return max(1, raw - self._player.get_damage_reduction())

    def _apply_damage(self, damage: int) -> Player:
        return self._player.take_damage(damage)

    def _is_dead(self, defender: Player) -> bool:
        return defender.is_dead()

    def _missed(self) -> dict[str, Any]:
        return self._update(
            self._player,
            f"The {self._enemy.name} attacked the player (a {self._player.type}), but missed.",
        )

    def _defender_wounded(self, defender: Player) -> dict[str, Any]:
        return self._update(
            defender,
            f"The {self._enemy.name} attacked the player (a {defender.type}) and wounded them."
            f"You must describe how the {self._enemy.name} attacked the player "
            f"and how the player was wounded. "
            "Do NOT say anything about the doorway out.",
        )

    def _defender_dead(self, defender: Player) -> dict[str, Any]:
        return self._update(
            defender,
            f"The {self._enemy.name} has killed the player (a {defender.type}). "
            "You must describe how the player was attacked. "
            "Describe the player's final moments. "
            "Do NOT say anything about what the player should do next.",
        )

    def _update(self, player: Player, msg: str) -> dict[str, Any]:
        narration = self._narrate(msg)
        return {
            "player": player,
            "dungeon": self._state.dungeon.with_room_updated(
                self._player.current_room_index, history=[narration]
            ),
            "narration": self._state.narration + [narration],
        }
