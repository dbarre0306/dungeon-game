"""Stand-ins for the game's non-deterministic collaborators: the two LLM agents
and the dice. Each is duck-typed to the one method the game calls on it."""

from dungeon_game.agents.dungeon_master_agent import DungeonMasterResponse
from dungeon_game.agents.router_agent import RouterState

_COMMAND_PREFIX = "Player command: "


class FakeRouterAgent:
    """Maps each player command to a scripted routing decision."""

    def __init__(self, routes: dict[str, RouterState]):
        self._routes = routes

    def invoke(self, msg: str) -> RouterState:
        command = msg.splitlines()[0].removeprefix(_COMMAND_PREFIX)
        if command not in self._routes:
            raise AssertionError(f"No route scripted for command: {command!r}")
        return self._routes[command]


class FakeDungeonMaster:
    """Narrates `[DM] <instruction>` and records every call.

    Echoing the instruction lets a test assert on what the game told the
    Dungeon Master to narrate, without depending on any LLM wording."""

    def __init__(self):
        self.calls: list[tuple[object, object, str]] = []

    @property
    def messages(self) -> list[str]:
        return [msg for _, _, msg in self.calls]

    def invoke(self, room, player, msg) -> DungeonMasterResponse:
        self.calls.append((room, player, msg))
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
