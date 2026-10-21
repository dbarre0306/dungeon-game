from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent
from dungeon_game.game_state import GameState


def describe_arrival(
    dungeon_master_agent: DungeonMasterAgent,
    state: GameState,
    preamble: str = "",
    include_command: bool = False,
) -> str:
    """Narrate a room the player has just arrived in, from its facts alone.
    `preamble` is extra direction placed ahead of the standard instruction."""
    msg = (
        f"{preamble}"
        "Describe the room to the player using only the room facts. "
        "The player needs to clearly understand what is there in order to make "
        "a decision on what to do next.  Do not invent new "
        "rooms, paths, exits, creatures, or other plot details that are "
        "not listed. If the facts or room history don't mention something, "
        "leave it out."
    )
    return dungeon_master_agent.invoke(
        state, msg, include_command=include_command
    ).narration
