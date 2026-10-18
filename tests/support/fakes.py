"""Stand-ins for the game's non-deterministic collaborators: the two LLM agents
and the dice. Each is duck-typed to the one method the game calls on it."""

import json

from dungeon_game.agents.dungeon_master_agent import DungeonMasterResponse
from dungeon_game.agents.router_agent import RouterState
from dungeon_game.domain.intent import IntentType, ShopItemName
from dungeon_game.game_state import GameState

_COMMAND_PREFIX = "Player command: "


class FakeRouterAgent:
    """Maps each player command to a scripted routing decision."""

    def __init__(self, routes: dict[str, RouterState]):
        self._routes = routes
        self.prompts: list[str] = []

    def invoke(
        self,
        msg: str,
        supported_intents: list[IntentType],
        shop_items: list[ShopItemName],
        enemy_name: str | None = None,
    ) -> RouterState:
        self.prompts.append(msg)
        quoted = msg.splitlines()[0].removeprefix(_COMMAND_PREFIX)
        command = json.loads(
            quoted.removeprefix("<player_command>").removesuffix("</player_command>")
        )
        if command not in self._routes:
            raise AssertionError(f"No route scripted for command: {command!r}")
        return self._routes[command]


class FakeDungeonMaster:
    """Narrates `[DM] <instruction>` and records every call.

    Echoing the instruction lets a test assert on what the game told the
    Dungeon Master to narrate, without depending on any LLM wording."""

    def __init__(self):
        self.calls: list[tuple[GameState, str]] = []
        self.included_command: list[bool] = []

    @property
    def messages(self) -> list[str]:
        return [msg for _, msg in self.calls]

    def invoke(self, state, msg, include_command=False) -> DungeonMasterResponse:
        self.calls.append((state, msg))
        self.included_command.append(include_command)
        return DungeonMasterResponse(narration=f"[DM] {msg}")


class FakeDice:
    """Returns scripted rolls in order and fails loudly if they run out or
    are left over, so a scenario cannot silently drift from its script."""

    def __init__(self, *rolls: int):
        self._rolls = list(rolls)

    def roll(self, num_sides: int) -> int:
        if not self._rolls:
            raise AssertionError(f"Unexpected roll(d{num_sides}): script exhausted")
        return self._rolls.pop(0)

    def assert_exhausted(self) -> None:
        assert not self._rolls, f"Unused scripted rolls: {self._rolls}"
