from abc import ABC, abstractmethod
from typing import Any

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.domain.dice import Dice
from dungeon_game.domain.rooms.combat_room import CombatRoom
from dungeon_game.game_state import GameState

# Simple d20 "hit" target: roll + to_hit_bonus >= HIT_TARGET means a hit
HIT_TARGET = 12


class AttackNode(ABC):
    """One side strikes at the other. `PlayerAttackNode` and `EnemyAttackNode` are mirror images."""

    _label: str

    def __init__(self, dungeon_master_agent: DungeonMasterAgent, dice: Dice | None = None):
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


class _Strike[Defender](ABC):
    """One attack: roll to hit, apply damage, narrate the result.

    Subclasses supply the attacker's rolls, how damage lands on the defender,
    and the narration prompt for each outcome."""

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
        defender = self._apply_damage(self._damage())
        if self._is_dead(defender):
            return self._defender_dead(defender)
        return self._defender_wounded(defender)

    @abstractmethod
    def _hits(self) -> bool: ...

    @abstractmethod
    def _damage(self) -> int: ...

    @abstractmethod
    def _apply_damage(self, damage: int) -> Defender:
        """The defender after taking `damage`."""

    @abstractmethod
    def _is_dead(self, defender: Defender) -> bool: ...

    @abstractmethod
    def _missed(self) -> dict[str, Any]: ...

    @abstractmethod
    def _defender_wounded(self, defender: Defender) -> dict[str, Any]: ...

    @abstractmethod
    def _defender_dead(self, defender: Defender) -> dict[str, Any]: ...

    def _narrate(self, msg: str) -> str:
        return self._dungeon_master_agent.invoke(self._room, self._player, msg).narration
