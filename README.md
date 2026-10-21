# Dungeon of Mistwood

A text-based dungeon crawler built as a LangGraph / LangChain demo, with a Gradio UI meant for deployment on Hugging Face Spaces.

**The quest:** a troll has stolen the **Amulet of Valdorin**. Fight through the dungeon and reclaim it.

You type what your character does in plain English ("I attack the goblin", "I buy a potion", "I go left") and a narrator, the Dungeon Master, describes what happens. The game rules live in code, not in the LLM: one model classifies what you typed, the code resolves it with real dice rolls and numbers, and a second model only narrates the result.

## The dungeon

The rooms form a one-way line. The challenge rooms are randomized each playthrough: 2 of the 3 (Monster, Trap, Treasure) appear, in random order.

```
Cave Entrance → Cave Chamber → (2 of: Monster Room, Trap Room, Treasure Room) → Shop Room → Throne Room
```

| Room          | What's there                                                              |
| ------------- | ------------------------------------------------------------------------- |
| Cave Entrance | Starting point. Enter the cave.                                           |
| Cave Chamber  | A fork: go left or right (flavor only, the route doesn't change).         |
| Monster Room  | A giant rat, goblin, or orc. Kill it to pass; it drops 5 gold.            |
| Trap Room     | A poison dart or swinging blade. Dodge it or take damage; gold on the far side. |
| Treasure Room | Two chests: one holds gold, the other a serpent.                          |
| Shop Room     | A merchant selling class-specific upgrades and potions.                   |
| Throne Room   | Final fight against a 30 HP troll holding the Amulet of Valdorin.         |

Each turn resolves a single action: look, move, attack, buy, drink a potion (Warrior), cast Heal (Mage), or open a chest. Compound commands are rejected, and actions that aren't legal in the current room are refused at no cost.

## Classes

|                | Warrior                      | Mage                |
| -------------- | ---------------------------- | ------------------- |
| HP             | 30                           | 18                  |
| Weapon         | Bronze sword + bronze shield | Staff (Fire bolt)   |
| To-hit bonus   | +3                           | +4                  |
| Damage         | 1d6 + 1                      | 1d6 + 2             |
| Starting gold  | 10                           | 10                  |
| Healing        | 2 potions (+8 HP each)       | 1 Heal cast         |

Combat is d20 + to-hit against a target of 12, with the player acting first and the enemy counterattacking. Shields absorb part of each enemy hit and wear down as they do.

> **Note:** both classes exist in the game logic, but the Gradio UI can currently only start a Warrior game.

A full playthrough is designed to take roughly 5 to 15 minutes. With sensible play the Warrior wins about 65–69% of runs and the Mage about 56–73%, depending on when they heal.

For the complete rules, balance numbers, and design notes, see [APP.md](APP.md).

## How it works

- **LangGraph** drives the game as a state machine: a node for each type of turn, with conditional edges for fighting vs. not and alive vs. dead.
- **LangChain** provides the chat model wrapper and structured output for two agents: a **Router** that classifies the player's text into an intent, and a **Dungeon Master** that narrates outcomes.
- **Gradio** provides the chat-style UI, with a status panel for HP, shield condition, potions, gold, and the current enemy's HP.
- **Pydantic** models hold all game state (player, dungeon, rooms, merchant). Nodes return updated copies rather than mutating state.

Each player command triggers one graph invocation: `Router → (Explore | Look | Attack | Shop | Heal | Open Chest | …) → Enemy Attack → Game Over`. Game state is held in memory per Gradio session, so closing the tab or restarting the server loses the game.

## Getting started

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

Create a `.env` file with your model provider key:

```
OPENAI_API_KEY=...
# Optional: defaults to gpt-4o-mini. A bare name means OpenAI;
# use provider:name for other providers.
MODEL=gpt-4o-mini
```

Launch the Gradio app:

```bash
uv run python app.py
```

## Development

```bash
uv run pytest            # run all tests
uv run ruff check .      # lint
uv run ruff format .     # format
```

## Project layout

```
app.py                      Gradio entry point
src/dungeon_game/
  game_graph.py             LangGraph workflow
  game_state.py             GameState model
  agents/                   Router and Dungeon Master agents
  nodes/                    One node per kind of turn
  domain/                   Actors, items, rooms, dungeon, dice, intents
  ui/                       Gradio home page, game view, session, theme
tests/                      pytest suite
```

## License

MIT. See [LICENSE](LICENSE).
