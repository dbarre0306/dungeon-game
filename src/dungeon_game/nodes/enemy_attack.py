from typing import Any

from dungeon_game.domain.actors.enemy import Enemy
from dungeon_game.domain.actors.player.player import Player
from dungeon_game.domain.rooms.combat_room import CombatRoom
from dungeon_game.game_state import GameState
from dungeon_game.nodes.attack import AttackNode, _Strike


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

    @property
    def _attacker(self) -> Enemy:
        return self._enemy

    @property
    def _defender(self) -> Player:
        return self._player

    def _on_defender_missed(self) -> dict[str, Any]:
        return self._update(
            self._player,
            f"The {self._enemy.name} attacked the player (a {self._player.type}), "
            "but missed.",
        )

    def _on_defender_unharmed(self, defender: Player) -> dict[str, Any]:
        defense = self._player.get_defense()
        absorbed_by = (
            f"the player's {defense} absorbed the blow and " if defense else ""
        )
        return self._update(
            defender,
            f"The {self._enemy.name} attacked the player (a {self._player.type}) "
            f"and hit, but {absorbed_by}the player took no damage. "
            "Do NOT say the player was wounded. "
            f"{self._defense_change(defender)}"
            "Do NOT say anything about the doorway out.",
        )

    def _on_defender_wounded(self, defender: Player) -> dict[str, Any]:
        return self._update(
            defender,
            f"The {self._enemy.name} attacked the player (a {defender.type}) "
            "and wounded them. "
            f"You must describe how the {self._enemy.name} attacked the player "
            "and how the player was wounded. "
            f"{self._defense_change(defender)}"
            "Do NOT say anything about the doorway out.",
        )

    def _on_defender_dead(self, defender: Player) -> dict[str, Any]:
        return self._update(
            defender,
            f"The {self._enemy.name} has killed the player (a {defender.type}). "
            "You must describe how the player was attacked. "
            "Describe the player's final moments.",
        )

    def _defense_change(self, defender: Player) -> str:
        change = defender.describe_defense_change(self._player)
        return f"{change} Mention it. " if change else ""

    def _update(self, player: Player, msg: str) -> dict[str, Any]:
        narration = self._narrate(msg)
        return {
            "player": player,
            "dungeon": self._state.dungeon.with_room_updated(
                self._player.current_room_index, history=[narration]
            ),
            "narration": self._state.narration + [narration],
        }
