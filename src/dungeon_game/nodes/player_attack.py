from typing import Any

from dungeon_game.domain.actors.enemy import Enemy
from dungeon_game.domain.actors.player.player import Player
from dungeon_game.domain.rooms.combat_room import CombatRoom
from dungeon_game.domain.rooms.monster_room import MonsterRoom
from dungeon_game.game_state import GameState
from dungeon_game.nodes.attack import AttackNode, _Strike


class PlayerAttackNode(AttackNode):
    """The player strikes at the enemy; `EnemyAttackNode` is its mirror image."""

    _label = "PLAYER ATTACK"

    def _early_result(self, state: GameState) -> dict[str, Any] | None:
        is_valid, err_msg = state.get_current_room().is_valid_intent(state.intent)
        if not is_valid:
            return self._narrate(err_msg, state)
        return None

    def _new_strike(self, state: GameState, room: CombatRoom) -> "_PlayerStrike":
        return _PlayerStrike(state, room, self._dungeon_master_agent, self._dice)

    def _narrate(self, msg: str, state: GameState) -> dict[str, Any]:
        response = self._dungeon_master_agent.invoke(state, msg)
        return {"narration": [response.narration]}


class _PlayerStrike(_Strike[Enemy]):
    """One player attack against the enemy."""

    @property
    def _attacker(self) -> Player:
        return self._player

    @property
    def _defender(self) -> Enemy:
        return self._enemy

    def _on_defender_missed(self) -> dict[str, Any]:
        return self._update(
            True,
            f"The player (a {self._player.type}) attacked the {self._enemy.name} "
            f"with a {self._player.offensive_weapon_payload}, but missed. "
            "Ignore the gold coins; stay focused on the battle. "
            "Do NOT say anything about the doorway out.",
        )

    def _on_defender_unharmed(self, defender: Enemy) -> dict[str, Any]:
        return self._update(
            True,
            f"The player (a {self._player.type}) attacked the {self._enemy.name} "
            f"with a {self._player.offensive_weapon_payload} and hit, "
            "but the blow did no "
            f"damage. Do NOT say the {self._enemy.name} was wounded. "
            "Ignore the gold coins; stay focused on the battle. "
            "Do NOT say anything about the doorway out.",
        )

    def _on_defender_wounded(self, defender: Enemy) -> dict[str, Any]:
        return self._update(
            True,
            f"The player (a {self._player.type}) attacked the {self._enemy.name} "
            f"with a {self._player.offensive_weapon_payload}.  "
            f"The {self._enemy.name} was wounded. "
            f"You must describe how the player attacked the {self._enemy.name} "
            f"and how the {self._enemy.name} was wounded. "
            "Ignore the gold coins; stay focused on the battle. "
            "Do NOT say anything about the doorway out.",
            enemy=defender,
        )

    def _on_defender_dead(self, defender: Enemy) -> dict[str, Any]:
        loot = self._room.gold_coins if isinstance(self._room, MonsterRoom) else 0
        looted = (
            f"The player then collected the {loot} gold coins behind the "
            f"{self._enemy.name}. "
            if loot
            else ""
        )
        return self._update(
            False,
            f"The player (a {self._player.type}) has killed the {self._enemy.name} "
            f"with a {self._player.offensive_weapon_payload}.  "
            f"You must describe how the player attacked the {self._enemy.name}. "
            "Stick to what it would feel like after a brutal battle. "
            f"{looted}"
            "Do say something about the doorway out.",
            gold=loot,
            enemy=defender,
            **({"gold_coins": 0} if loot else {}),
        )

    def _update(
        self, is_fighting: bool, msg: str, gold: int = 0, **room_updates: Any
    ) -> dict[str, Any]:
        narration = self._narrate(msg)
        return {
            "player": self._player.model_copy(
                update={
                    "is_fighting": is_fighting,
                    "gold_coins": self._player.gold_coins + gold,
                }
            ),
            "dungeon": self._state.dungeon.with_room_updated(
                self._player.current_room_index, history=[narration], **room_updates
            ),
            "narration": [narration],
        }
