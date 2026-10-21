"""One player's game in progress: the game state plus what the page shows."""

import logging
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Literal

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.agents.router_agent import RouterAgent
from dungeon_game.domain.actors.merchant import Merchant
from dungeon_game.domain.actors.player.mage import create_default_mage
from dungeon_game.domain.actors.player.player import Player
from dungeon_game.domain.actors.player.warrior import create_default_warrior
from dungeon_game.domain.dungeon.dungeon_factory import DungeonFactory
from dungeon_game.game_graph import GameGraph
from dungeon_game.game_state import GameState

logger = logging.getLogger(__name__)

OPENING_COMMAND = "look around"
ERROR_MESSAGE = (
    "The narrator lost the thread of the story. "
    "Check the model settings and your API key, then try your action again."
)

HERO_FACTORIES: dict[str, Callable[[], Player]] = {
    "warrior": create_default_warrior,
    "mage": create_default_mage,
}

EntryKind = Literal["command", "narration", "error"]


@dataclass(frozen=True)
class LogEntry:
    kind: EntryKind
    text: str


@dataclass
class Session:
    state: GameState
    log: list[LogEntry] = field(default_factory=list)
    # A command waiting for the narrator; the page shows it as in progress.
    pending: str | None = None


@lru_cache(maxsize=1)
def get_graph() -> GameGraph:
    """Build the game graph on first use, so the home page loads without a key."""
    model_name = os.getenv("MODEL", "gpt-4o-mini")
    # A bare name defaults to OpenAI; "provider:name" is used as given.
    model = model_name if ":" in model_name else f"openai:{model_name}"
    return GameGraph(RouterAgent(model), DungeonMasterAgent(model))


def start_session(class_key: str) -> Session:
    """A fresh dungeon and hero, waiting for the narrator to open the scene."""
    if class_key not in HERO_FACTORIES:
        raise ValueError(f"Cannot start a game as {class_key!r}")
    player = HERO_FACTORIES[class_key]()
    merchant = Merchant(merchandise=player.get_supported_merchandise())
    dungeon = DungeonFactory().generate(merchant)
    state = GameState(
        player=player, dungeon=dungeon, command=OPENING_COMMAND, opening=True
    )
    return Session(state=state, pending=OPENING_COMMAND)


def queue_command(session: Session, text: str) -> Session:
    """Record what the player typed. Blank input, a turn already under way, or a
    finished game changes nothing."""
    text = text.strip()
    if not text or session.pending or session.state.game_over:
        return session
    session.log.append(LogEntry("command", text))
    session.pending = text
    return session


def resolve_pending(session: Session, graph: GameGraph | None = None) -> Session:
    """Play out the queued command and add the narration to the log."""
    command = session.pending
    if command is None:
        return session
    session.pending = None
    try:
        graph = graph or get_graph()
        state = graph.invoke(session.state.model_copy(update={"command": command}))
    except Exception:
        # Details stay in the server log: provider errors can echo credentials.
        logger.exception("Turn failed for command %r", command)
        session.log.append(LogEntry("error", ERROR_MESSAGE))
        return session
    session.state = state
    session.log.extend(LogEntry("narration", text) for text in state.narration)
    return session
