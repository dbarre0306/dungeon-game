# Dungeon of Mistwood

A text-based dungeon crawler — design notes for a LangGraph / LangChain demo app, deployed with Gradio on Hugging Face Spaces.

**The quest:** a troll has stolen the **Amulet of Valdorin**. The player's goal is to fight through the dungeon and reclaim it.

---

## Part 1 — The Game

### Overview

This is a short, text-based dungeon crawler in the style of a choose-your-own-adventure story. The player reads narration, types what their character does in plain English, and a narrator (the "DM") describes what happens next. There's no board and no rules to memorize — combat, exploration, and shopping are all resolved through short text exchanges, with dice rolls determining outcomes behind the scenes.

### The Dungeon

The dungeon is a small, fixed set of rooms, but the sequence of challenge rooms is randomized each playthrough. At the Fork, the player can go left or right — this choice is flavor only. Either way, the game randomly picks **2 of 3 possible challenge rooms** (Goblin Room, Trap Room, Treasure Room — no repeats), in random order, before a guaranteed stop at the Shop and the final Boss Room.

**Path:** `Cave Entrance → Fork → (2 of 3: Goblin Room, Trap Room, Treasure Room, in random order) → Shop Room → Boss Room`

| Room          | What's there                                                                                                |
| ------------- | ----------------------------------------------------------------------------------------------------------- |
| Cave Entrance | Starting point. A torch on the wall.                                                                        |
| Fork          | Tunnel splits left/right — cosmetic only; triggers the random challenge sequence either way.                |
| Goblin Room   | A random enemy: goblin, orc, or giant rat. Drops 10 gold.                                                   |
| Trap Room     | A dart or swinging blade (random) — dodge it or take damage. Gold is visible across the room either way.    |
| Treasure Room | Two chests — one gold, one a hidden serpent.                                                                |
| Shop Room     | A merchant selling class-specific upgrades and potions. Always visited, guaranteeing a place to spend gold. |
| Boss Room     | Final fight: the troll holding the Amulet of Valdorin.                                                      |

Exactly 2 of the 3 challenge rooms appear in any given run — the third is simply skipped that time. This keeps every playthrough a little different while guaranteeing the Shop is always reachable, so gold earned earlier always has somewhere to go.

**Trap Room details.** The trap is randomly either a dart trap or a swinging blade — not a pit, so it never stops the player from moving on. It triggers automatically the moment the player enters the room, no input required: a dice roll decides whether they dodge it cleanly or get hit and lose some HP. As they step forward, they see gold coins glinting on the far wall — reaching them is what triggers the trap, but the coins are collected regardless of whether the trap hits or misses. There's no "stuck and must escape" mechanic — it's a one-time crossing, not an ongoing obstacle.

**Treasure Room details.** Two chests are present — one holds real loot (gold and a potion), the other has a serpent coiled inside that strikes when opened. Which chest is which is randomized once, when the player enters the room, and stays fixed for that playthrough. The player picks a chest by name (e.g. "open the left chest") without knowing in advance which is safe.

### Playable Roles

Two classes are available for this demo: **Warrior** and **Mage**. Each starts with fixed gear and stats — no character building or leveling required.

|                | Warrior                                     | Mage                  |
| -------------- | ------------------------------------------- | --------------------- |
| Starting HP    | 25                                          | 15                    |
| Weapon         | Sword + shield                              | Staff                 |
| To-hit bonus   | +3                                          | +2                    |
| Damage die     | 1d6                                         | 1d8 (Firebolt)        |
| Special        | Shield passively lowers chance of being hit | Can cast Heal (+8 HP) |
| Starting gold  | 10                                          | 5                     |
| Starting items | Sword, shield, 2 potions                    | Staff, 1 potion       |

**Shop upgrades** (class-specific, so each class is only offered relevant gear):

- Warrior: **Steel Sword** (+2 damage), **Reinforced Shield** (further reduces chance of being hit)
- Mage: **Elder Staff** (+2 damage)
- Either class: **Potion** (+8 HP, usable anytime)

### What the Player Does

At the start, the player picks a class (Warrior or Mage) and is dropped into the Cave Entrance. From there, each turn follows the same loop:

1. The DM describes the current scene.
2. The player types what they want to do, in plain English (e.g. "I attack the goblin," "I buy a potion," "I go left").
3. The game figures out what kind of action that is (fighting, shopping, talking, exploring) and resolves it — rolling dice where the outcome is uncertain.
4. The DM narrates the result, and the player's HP / inventory / gold sidebar updates to match.

The player can type anything, but each turn resolves a **single action**. If someone types a compound action (e.g. "drink a potion and attack the troll"), the game resolves just the first one and narrates accordingly — keeps combat math and the graph's logic simple, one action in, one resolved turn out.

### Combat

Combat is a back-and-forth exchange resolved with two dice rolls per attack: a 20-sided die decides whether an attack lands (roll + class's to-hit bonus, compared against a target number), and if it hits, a smaller die decides how much damage is dealt. After the player's attack resolves, the enemy immediately gets its own attack in the same turn, using the same two-roll process. One full player turn — attack, outcome, enemy counterattack, outcome — is resolved and narrated together as a single response.

### Winning and Losing

- **Lose:** the player's HP reaches 0 at any point — the game ends immediately with a death narration.
- **Win:** the player defeats the troll in the Boss Room and reclaims the **Amulet of Valdorin**, ending the run with a victory narration. Victory also grants 50 gold, found on the troll.

### Session Length

A full playthrough — Cave Entrance through the boss fight — is designed to take roughly **5 to 15 minutes**, short enough to finish in one sitting while still passing through exploration, a random encounter or trap, a shop stop, and a final fight.

---

## Part 2 — Implementation (High Level)

### Tech Stack

- **LangGraph** — the state machine that drives the game: nodes for each type of turn, conditional edges for branching (hit vs. miss, alive vs. dead, in-budget vs. not).
- **LangChain** — underlying building blocks used inside the graph: the chat model wrapper, tool definitions, and the bridge that turns MCP tools into usable LangChain tools.
- **MCP (Model Context Protocol)** — used for the dice-rolling tool (and optionally a lore/flavor-text tool), so outcomes are resolved by real code rather than left to the LLM to invent.
- **Gradio** — the chat-style UI, deployed as a Hugging Face Space, with a sidebar showing HP, inventory, and gold.
- **Persistence** — LangGraph's checkpointer (SQLite-backed) saves game state per player session (`thread_id`), so a player can leave and resume later.

### Design Principle: Data vs. Narration

The dungeon's rooms, enemies, stats, and shop items are all defined as fixed data (a Python structure), not invented by the LLM. Graph nodes read and update this data directly — checking real numbers like enemy HP — while the LLM's only job is to turn those numbers into narration. This keeps the conditional edges reliable and the game state consistent across turns.

### The Workflow Graph

Each player command triggers exactly one graph invocation — input goes in, flows through the relevant nodes, and a single narrated response comes out. The graph looks roughly like this:

1. **Router Node** — classifies the player's free-text input as explore, combat, dialogue, or shop, and routes to the matching node.
2. **Explore Node** — default handling for movement and looking around; generates the randomized 2-of-3 challenge sequence at the Fork, tracks the player's position in that sequence, and resolves room transitions and traps.
3. **Combat Node** — resolves the player's attack (calls the dice MCP tool), then the enemy's counterattack, updating HP for both sides.
4. **Shop Node** — checks gold against item price, updates inventory and gold if the purchase is valid.
5. **Game Over Node** — reached only via a conditional check (HP ≤ 0 for either side) after combat; ends the session or triggers the victory narration and reward.

**Example — an attack turn:** the longest realistic path through the graph in a single turn — a player attack that results in a kill — looks like: `Router → Combat Node → Game Over Node`. Most turns are shorter, resolving in just `Router → one node`, since the "did someone just die" check is the only case that chains a third node.

### Persistence Flow

Each play session is tied to a `thread_id`. Every graph invocation reads the current state (HP, inventory, gold, current room) from the checkpointer at the start and writes the updated state back out at the end. This is what allows a player to close the browser tab and resume later with their character and progress intact, and it doubles as a clean, concrete example of LangGraph's persistence model.

---

## Part 3 — Weekly Plan

Assumes a few dedicated part-time weeks (not full-time sprints).

### Week 1 — Core graph, no tools yet

- Learn LangGraph basics: `StateGraph`, nodes, `add_conditional_edges`
- Build the skeleton: router → explore → combat → shop, with simple conditionals (HP check, intent check)
- Run it in plain Python via console input — no Gradio yet
- Highest-value learning week; most of the "aha" moments about LangGraph happen here

### Week 2 — Persistence + Gradio

- Add SQLite-backed checkpointing; learn `thread_id` semantics; test save/resume
- Wire up a basic Gradio chat interface (chat window + HP/inventory/gold sidebar)
- Get "New Game" vs. "Continue" working end-to-end locally, using the Space's regular filesystem for the save file

### Week 3 — MCP tools

- Stand up a simple MCP server (a dice roller is a great first one)
- Wire it in via `langchain-mcp-adapters` / `MultiServerMCPClient`
- Add a second tool (e.g. a flavor-text or name generator) to prove out multi-tool routing
- Highest-risk week for unexpected debugging (async/transport issues between MCP and LangGraph)

### Week 4 — Polish + deploy

- Deploy to Hugging Face Spaces
- If true cross-restart persistence is wanted, swap the save file's path to a mounted Storage Bucket — no other code changes needed
- UI polish, error handling for bad LLM outputs breaking the state machine
- Buffer time for the inevitable "one thing doesn't work like the docs say" issue

**Scope risk to watch:** it's tempting to spend extra time making the _game_ better (more rooms, more balance tuning), but the actual goal is learning the _framework_. Keep gameplay content to what's outlined in Part 1 and resist expanding it until the graph itself is solid.
