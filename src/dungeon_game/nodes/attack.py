from abc import ABC, abstractmethod
from typing import Any

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.domain.actors.combatant import Combatant
from dungeon_game.domain.dice import Dice
from dungeon_game.domain.rooms.combat_room import CombatRoom
from dungeon_game.game_state import GameState

# Simple d20 "hit" target: roll + hit_bonus >= HIT_TARGET means a hit
HIT_TARGET = 12


class AttackNode(ABC):
    """One side strikes at the other.

    `PlayerAttackNode` and `EnemyAttackNode` are mirror images.
    """

    _label: str

    def __init__(
        self, dungeon_master_agent: DungeonMasterAgent, dice: Dice | None = None
    ):
        self._dungeon_master_agent = dungeon_master_agent
        self._dice = dice or Dice()

    def execute(self, state: GameState) -> dict[str, Any]:
        print(self._label)
        early_result = self._early_result(state)
        if early_result is not None:
            return early_result
        return self._new_strike(state, self._get_combat_room(state)).resolve()

    @abstractmethod
    def _early_result(self, state: GameState) -> dict[str, Any] | None:
        """A state update that ends the node before any strike, or None to carry on."""

    @abstractmethod
    def _new_strike(self, state: GameState, room: CombatRoom) -> "_Strike":
        """The strike this node resolves."""

    @staticmethod
    def _get_combat_room(state: GameState) -> CombatRoom:
        room = state.get_current_room()
        if not isinstance(room, CombatRoom):
            raise TypeError("The room must be a CombatRoom")
        return room


class _Strike[Defender: Combatant](ABC):
    """One attack: roll to hit, apply damage, narrate the result.

    Subclasses say who attacks and who defends, and supply the narration prompt
    for each outcome."""

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

    # Only the player's own strike is narrated using their command
    _include_command = False

    def resolve(self) -> dict[str, Any]:
        if not self._is_defender_hit():
            return self._on_defender_missed()
        raw = self._raw_damage_points()
        damage = max(0, raw - self._defender.reduced_defensive_weapon_damage)
        defender = self._defender.with_defense_worn(raw - damage)
        if damage == 0:
            return self._on_defender_unharmed(defender)
        defender = defender.with_damage(damage)
        if defender.is_dead():
            return self._on_defender_dead(defender)
        return self._on_defender_wounded(defender)

    @property
    @abstractmethod
    def _attacker(self) -> Combatant: ...

    @property
    @abstractmethod
    def _defender(self) -> Defender: ...

    def _is_defender_hit(self) -> bool:
        return self._dice.roll(20) + self._attacker.hit_bonus >= HIT_TARGET

    def _raw_damage_points(self) -> int:
        return self._dice.roll(6) + self._attacker.additional_offensive_weapon_damage

    @abstractmethod
    def _on_defender_missed(self) -> dict[str, Any]: ...

    @abstractmethod
    def _on_defender_unharmed(self, defender: Defender) -> dict[str, Any]:
        """A hit that was fully absorbed (e.g. by armor), so no health was lost.
        `defender` is the defender after its defense wore down."""

    @abstractmethod
    def _on_defender_wounded(self, defender: Defender) -> dict[str, Any]: ...

    @abstractmethod
    def _on_defender_dead(self, defender: Defender) -> dict[str, Any]: ...

    def _narrate(self, msg: str) -> str:
        return self._dungeon_master_agent.invoke(
            self._state, msg, include_command=self._include_command
        ).narration
