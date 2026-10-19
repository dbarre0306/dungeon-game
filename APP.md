# Dungeon of Mistwood

A text-based dungeon crawler — design notes for a LangGraph / LangChain demo app, deployed with Gradio on Hugging Face Spaces.

**The quest:** a troll has stolen the **Amulet of Valdorin**. The player's goal is to fight through the dungeon and reclaim it.

---

## Part 1 — The Game

### Overview

This is a short, text-based dungeon crawler in the style of a choose-your-own-adventure story. The player reads narration, types what their character does in plain English, and a narrator (the "DM") describes what happens next. There's no board and no rules to memorize — combat, exploration, and shopping are all resolved through short text exchanges, with dice rolls determining outcomes behind the scenes.

### The Dungeon

The dungeon is a small, fixed set of rooms, but the sequence of challenge rooms is randomized each playthrough. At the Fork, the player can go left or right — this choice is flavor only. Either way, the game randomly picks **2 of 3 possible challenge rooms** (Monster Room, Trap Room, Treasure Room — no repeats), in random order, before a guaranteed stop at the Shop and the final Throne Room.

**Path:** `Cave Entrance → Fork → (2 of 3: Monster Room, Trap Room, Treasure Room, in random order) → Shop Room → Throne Room`

| Room          | What's there                                                                                                |
| ------------- | ----------------------------------------------------------------------------------------------------------- |
| Cave Entrance | Starting point. A torch on the wall.                                                                        |
| Fork          | Tunnel splits left/right — cosmetic only; triggers the random challenge sequence either way.                |
| Monster Room  | A random enemy: goblin, orc, or giant rat. Drops 10 gold.                                                   |
| Trap Room     | A dart or swinging blade (random) — dodge it or take damage. Gold is visible across the room either way.    |
| Treasure Room | Two chests — one gold, one a hidden serpent.                                                                |
| Shop Room     | A merchant selling class-specific upgrades and potions. Always visited, guaranteeing a place to spend gold. |
| Throne Room   | Final fight: a 30 HP troll with a spiked club, holding the Amulet of Valdorin. Hits much harder than others. |

Exactly 2 of the 3 challenge rooms appear in any given run — the third is simply skipped that time. This keeps every playthrough a little different while guaranteeing the Shop is always reachable, so gold earned earlier always has somewhere to go.

**Trap Room details.** The trap is randomly either a dart trap or a swinging blade — not a pit, so it never stops the player from moving on. The passageway forward and some gold coins are on the opposite side of the room. The trap triggers automatically the moment the player attempts to cross the room. A dice roll decides whether they dodge it cleanly, suffer a minor wound, or a major wound. There's no "stuck and must escape" mechanic — it's a one-time crossing, not an ongoing obstacle. The die to determine if the player is struck is the same as the monster room. Another die with ten sides determine the extent of the wound. If it is eight or greater, then it is a major wound (5 HP); otherwise a minor wound (2 HP). A player who survives the trap automatically collects the gold coins on the far side: a random 4 to 6.

**Treasure Room details.** Two identical chests sit to the left and right of the passageway forward — one holds real loot (gold coins), the other has a serpent coiled inside that strikes when opened. Which chest is which is randomized once, when the player enters the room, and stays fixed for that playthrough. The player must name the chest to open (e.g. "open the left chest") without knowing in advance which is safe. If the command doesn't specify a chest (e.g. just "open the chest"), the DM tells the player they must say which chest to open, and nothing else happens. They can open only one chest, never both.

- **Gold chest:** the player is awarded a random 3 to 6 gold coins the moment they open it. Nothing else happens, and the player is free to leave the room.
- **Serpent chest:** combat begins immediately. The serpent starts with 15 HP (tracked internally — the player is not told its HP) and fights using the same logic as the monster room — the same to-hit roll and damage die as the monsters, with the player's attack followed by the serpent's counterattack each turn, until one of them dies. Only when the player opens this chest does the narration tell them they must kill the serpent. Killing it allows the player to leave, but earns no gold, and the other chest stays closed.
- **Trying to leave while the serpent is alive:** the player cannot leave. The attempt costs them their turn, and the serpent can strike them.
- **Trying to leave before opening a chest:** the player cannot leave until they open one. The attempt is simply refused, with no penalty.
- If the player's HP reaches 0 in the fight, the game ends as usual.

**Shop Room details.** An old merchant selling stuff.

- **Stock depends on the class:**
  - Warrior: one steel sword, one steel shield, and three potions.
  - Wizard: the Elder staff, which has more powerful firebolt spells. No potions.
- **Prices:**
  - Potion: 5 gold coins.
  - Steel sword: 10 gold coins.
  - Steel shield: 10 gold coins.
  - Elder staff: 20 gold coins.
- **Upgrades replace old gear:** buying a steel sword automatically discards the bronze sword. The same goes for the shield and the staff.
- **Potions add up:** bought potions are added to any potions the player already has.
- **Quantity:**
  - Potions are the only item that can be bought in quantity (e.g. "buy 2 potions").
  - If the player doesn't say how many, they buy one.
- **Limited stock:** the merchant tracks how many of each item are left, and an item that runs out (e.g. the steel sword once bought) can't be bought again.
- **All or nothing:** if the player asks for more than the merchant has left, or can't afford the total, nothing is bought and the merchant says why.
- **Leaving:** the player is not required to buy anything. At any point, the player can move forward to the next room.

**Throne Room details.** The final room. A troll twice the player's size sits on a stone throne, a large spiked wooden club in its hand and the Amulet of Valdorin hanging around its neck.

- **The troll:** armed with a large spiked wooden club. 30 HP (tracked internally — the player is not told its HP). It fights using the same logic as the monster room — the same to-hit roll as the monsters, with the player's attack followed by the troll's counterattack each turn, until one of them dies.
- **The troll hits much harder than other enemies.** Its club deals a bigger damage die than anything else in the dungeon: 1d10 + 2 (placeholder — HP and damage numbers are expected to be tuned later).
- **No exit:** there is no way out of this room. The player's only goal is to kill the troll. If the player tries to leave or go anywhere, the DM tells them there is no way out and nothing else happens.
- **Winning:** the moment the troll's HP reaches 0, the player wins. The narration simply tells the player that they have taken the amulet from the troll's neck. The amulet has the power to bring the player back to the kingdom, so the victory narration ends with the player being carried home. The amulet is not a separate pickup action and is not added to the inventory.
- If the player's HP reaches 0 first, the game ends as usual.

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
| Starting items | Sword, shield, 2 potions                    | Staff                 |

**Shop upgrades** (class-specific, so each class is only offered relevant gear):

- Warrior: **Steel Sword** (+2 damage), **Steel Shield** (further reduces chance of being hit), **Potion** (+8 HP, usable anytime)
- Mage: **Elder Staff** (+2 damage)

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
- **Win:** the player defeats the troll in the Throne Room (its HP reaches 0) and reclaims the **Amulet of Valdorin** automatically — the narration tells them they have taken it from the troll's neck. The amulet's power then brings the player back to the kingdom, ending the run with a victory narration.

### Session Length

A full playthrough — Cave Entrance through the troll fight — is designed to take roughly **5 to 15 minutes**, short enough to finish in one sitting while still passing through exploration, a random encounter or trap, a shop stop, and a final fight.

---

## Part 2 — Implementation (High Level)

### Tech Stack

- **LangGraph** — the state machine that drives the game: nodes for each type of turn, conditional edges for branching (hit vs. miss, alive vs. dead, in-budget vs. not).
- **LangChain** — underlying building blocks used inside the graph: the chat model wrapper, tool definitions, etc.
- **Gradio** — the chat-style UI, deployed as a Hugging Face Space, with a sidebar showing HP, inventory, and gold.
- **Persistence** — LangGraph's checkpointer (SQLite-backed) saves game state per player session (`thread_id`), so a player can leave and resume later.

### Design Principle: Data vs. Narration

The dungeon's rooms, enemies, stats, and the merchant's stock are all defined as fixed data (a Python structure), not invented by the LLM. Graph nodes read and update this data directly — checking real numbers like enemy HP — while the LLM's only job is to turn those numbers into narration. This keeps the conditional edges reliable and the game state consistent across turns.

### The Workflow Graph

Each player command triggers exactly one graph invocation — input goes in, flows through the relevant nodes, and a single narrated response comes out. The graph looks roughly like this:

1. **Router Node** — classifies the player's free-text input as explore, combat, dialogue, or shop, and routes to the matching node.
2. **Explore Node** — default handling for movement and looking around; generates the randomized 2-of-3 challenge sequence at the Fork, tracks the player's position in that sequence, and resolves room transitions and traps.
3. **Combat Node** — resolves the player's attack, then the enemy's counterattack, updating HP for both sides.
4. **Shop Node** — checks the merchant's remaining stock and the player's gold against the price; if the purchase is valid, it hands the item to the player, deducts the gold, and reduces the merchant's stock.
5. **Game Over Node** — reached only via a conditional check (HP ≤ 0 for either side) after combat; ends the session or triggers the victory narration and reward.

**Example — an attack turn:** the longest realistic path through the graph in a single turn — a player attack that results in a kill — looks like: `Router → Combat Node → Game Over Node`. Most turns are shorter, resolving in just `Router → one node`, since the "did someone just die" check is the only case that chains a third node.

### Persistence Flow

Each play session is tied to a `thread_id`. Every graph invocation reads the current state (HP, inventory, gold, current room, the merchant's remaining stock) from the checkpointer at the start and writes the updated state back out at the end. This is what allows a player to close the browser tab and resume later with their character and progress intact, and it doubles as a clean, concrete example of LangGraph's persistence model.
