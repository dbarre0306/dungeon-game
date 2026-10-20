# Dungeon of Mistwood

A text-based dungeon crawler — design notes for a LangGraph / LangChain demo app, deployed with Gradio on Hugging Face Spaces.

**The quest:** a troll has stolen the **Amulet of Valdorin**. The player's goal is to fight through the dungeon and reclaim it.

---

## Part 1 — The Game

### Overview

This is a short, text-based dungeon crawler in the style of a choose-your-own-adventure story. The player reads narration, types what their character does in plain English, and a narrator (the "DM") describes what happens next. There's no board and no rules to memorize — combat, exploration, and shopping are all resolved through short text exchanges, with dice rolls determining outcomes behind the scenes. The game rules live in code, not in the LLM: one model classifies what the player typed, the code resolves it with real numbers, and a second model only narrates the result.

### The Dungeon

The dungeon is a small, fixed set of rooms, but the sequence of challenge rooms is randomized each playthrough. The whole dungeon is generated up front when the game starts. At the Cave Chamber (the fork), the player must say left or right — this choice is flavor only and does not change the route. The game randomly picks **2 of 3 possible challenge rooms** (Monster Room, Trap Room, Treasure Room — no repeats), in random order, before a guaranteed stop at the Shop and the final Throne Room.

**Path:** `Cave Entrance → Cave Chamber → (2 of 3: Monster Room, Trap Room, Treasure Room, in random order) → Shop Room → Throne Room`

The rooms form a one-way line: the player only ever moves forward, and there is no going back. In every room the player can _look_ around, and can drink a potion (Warrior) or cast Heal (Mage); other actions depend on the room, as described below.

**Legal actions.** Each room has a fixed set of legal intents (listed below). If the player types something outside that set, the DM tells them it can't be done here and nothing else happens: no state changes, no dice, and no counterattack, even in a fight. A _legal_ intent can still fail: the exit is blocked, the wrong direction is given, no chest is named, the player can't afford the item, has no potions left, or names a weapon they don't carry. A failed attempt is narrated and changes nothing, but during a fight the enemy still counterattacks (see _Combat_).

| Room          | What's there                                                                                                                                   |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Cave Entrance | Starting point. The player must enter the cave (move forward); any other direction is refused.                                                 |
| Cave Chamber  | The fork. A torch on the wall and a passage left and right. The player must pick left or right ("forward" is refused); the choice is cosmetic. |
| Monster Room  | A random enemy: giant rat, goblin, or orc (stats in _Game Balance_). Drops 5 gold.                                                             |
| Trap Room     | A poison dart or swinging blade (random) — dodge it or take damage. Gold is visible across the room either way.                                |
| Treasure Room | Two chests — one gold, one a hidden serpent.                                                                                                   |
| Shop Room     | A merchant selling class-specific upgrades and potions. Always visited, guaranteeing a place to spend gold.                                    |
| Throne Room   | Final fight: a 25 HP troll with a spiked club, holding the Amulet of Valdorin. Hits much harder than others.                                   |

| Room          | Legal intents                          |
| ------------- | -------------------------------------- |
| Cave Entrance | look, move, heal                       |
| Cave Chamber  | look, move, heal                       |
| Monster Room  | look, move, attack, heal               |
| Trap Room     | look, move, heal                       |
| Treasure Room | look, move, attack, open a chest, heal |
| Shop Room     | look, move, buy, heal                  |
| Throne Room   | look, move, attack, heal               |

Heal means drinking a potion (Warrior) or casting Heal (Mage). Anything else, including the "multiple" and "unknown" commands described under _What the Player Does_, is illegal in that room.

**Monster Room details.** The player enters the room already in a fight. The monster will not let the player pass while it is alive, so the only way on is to kill it; there is no going back. Each exchange follows the _Combat_ rules. When the monster dies, the player automatically collects the 5 gold coins behind it and the doorway forward opens. Attacking a monster that is already dead is refused.

Exactly 2 of the 3 challenge rooms appear in any given run — the third is simply skipped that time. This keeps every playthrough a little different while guaranteeing the Shop is always reachable, so gold earned earlier always has somewhere to go.

**Trap Room details.** The trap is randomly either a poison dart or a swinging blade — not a pit, so it never stops the player from moving on. The passageway forward and some gold coins are on the opposite side of the room. In this room the only actions that do anything are moving forward, looking around, and healing (drink a potion or cast Heal); anything else is not understood. Healing here costs only the turn, since there is no counterattack. Left and right are refused. The trap triggers automatically the moment the player tries to cross the room. The shield does not reduce trap damage, and the shield loses no durability to it. There's no "stuck and must escape" mechanic — it's a one-time crossing, not an ongoing obstacle. The game rolls a d20 (no bonus): **11 or lower dodges the trap** (55% of the time); **12 or higher strikes the player** (45%). When struck, a d10 decides the extent of the wound: 8 or greater is a major wound (5 HP); otherwise a minor wound (2 HP). A player who survives the trap — whether they dodged it or were wounded — automatically collects the gold coins on the far side: a random 4 to 6 (3 + a d3). If the wound kills the player, the game ends.

**Treasure Room details.** Two identical chests sit to the left and right of the passageway forward — one holds real loot (gold coins), the other has a serpent coiled inside that strikes when opened. Which chest is which is randomized once, when the dungeon is generated, and stays fixed for that playthrough. The player must name the chest to open (e.g. "open the left chest") without knowing in advance which is safe. If the command doesn't specify a chest (e.g. just "open the chest"), the DM tells the player they must say which chest to open, and nothing else happens. They can open only one chest, never both; trying to open the other one afterwards is refused. If the serpent is loose when that happens, the attempt costs the player their turn and the serpent gets a free attack.

- **Gold chest:** the player is awarded a random 3 to 6 gold coins (2 + a d4) the moment they open it. Nothing else happens, and the player is free to leave the room.
- **Serpent chest:** combat begins immediately. The serpent starts with 12 HP and fights using the same logic as the monster room — the serpent's stats are in _Game Balance_, with the player's attack followed by the serpent's counterattack each turn, until one of them dies. The serpent does not bite on the turn the chest is opened; the narration just tells the player they must kill it. Killing it allows the player to leave, but earns no gold, and the other chest stays closed.
- **Trying to leave while the serpent is alive:** the player cannot leave. The attempt costs them their turn, and the serpent gets a free attack. Attacking is only possible while the serpent is loose; otherwise there is nothing to attack.
- **Trying to leave before opening a chest:** the player cannot leave until they open one. The attempt is simply refused, with no penalty.
- If the player's HP reaches 0 in the fight, the game ends as usual.

**Shop Room details.** An old merchant behind a two-wheeled wooden cart, selling stuff. The player can look around, buy, move forward, or heal (drink a potion or cast Heal); trying to attack the merchant is refused (he is peaceful).

- **Stock depends on the class:**
  - Warrior: one steel sword, one steel shield, and three potions.
  - Mage: the Elder staff, which has more powerful firebolt spells. No potions (the Mage has Heal instead).
- **Prices:**
  - Potion: 5 gold coins.
  - Steel sword: 10 gold coins.
  - Steel shield: 10 gold coins.
  - Elder staff: 15 gold coins.
- **Upgrades replace old gear:** buying a steel sword automatically discards the bronze sword. The same goes for the shield (the new shield arrives in full condition) and the staff. The Elder staff keeps any Heal casts the old staff had left, and adds its own 2 on top (so a Mage who has not cast any arrives with 3).
- **Potions add up:** bought potions are added to any potions the player already has.
- **Quantity:**
  - The player names one kind of item per purchase and may give a number (e.g. "buy 2 potions"). Only potions have more than one in stock.
  - If the player doesn't say how many, they buy one. A quantity below one is refused.
  - If the player doesn't say what they want to buy, the merchant asks.
- **Limited stock:** the merchant tracks how many of each item are left, and an item that runs out (e.g. the steel sword once bought) can't be bought again.
- **All or nothing:** if the player asks for more than the merchant has left, or can't afford the total, nothing is bought and the merchant says why.
- **Leaving:** the player is not required to buy anything. At any point, the player can move forward to the next room.
- There is no rest by the fire or any other free healing here.

**Throne Room details.** The final room. A troll twice the player's size sits on a stone throne, a large spiked wooden club in its hand and the Amulet of Valdorin hanging around its neck.

- **The troll:** twice the player's size and armed with a large spiked wooden club. 25 HP. It fights using the same logic as the monster room — the same to-hit rules as the monsters, with the player's attack followed by the troll's counterattack each turn, until one of them dies. The player enters the room already in a fight.
- **The troll hits much harder than other enemies.** Its club deals more damage than anything else in the dungeon: 1d8 + 2 (see _Game Balance_).
- **No exit:** there is no way out of this room. The player's only goal is to kill the troll. If the player tries to leave or go anywhere, the DM tells them there is no way out, and the troll counterattacks like it does after any other command during the fight.
- **Winning:** the moment the troll's HP reaches 0, the player wins — the troll does not get a final counterattack. The narration simply tells the player that they have taken the amulet from the troll's neck. The amulet has the power to bring the player back to the kingdom, so the victory narration ends with the player being carried home. The amulet is not a separate pickup action and is not added to the inventory.
- If the player's HP reaches 0 first, the game ends as usual.

### Playable Roles

Two classes are available for this demo: **Warrior** and **Mage**. Each starts with fixed gear and stats — no character building or leveling required.

|                  | Warrior                      | Mage                   |
| ---------------- | ---------------------------- | ---------------------- |
| Maximum HP       | 30                           | 24                     |
| Starting HP      | 30                           | 24                     |
| Weapon           | Bronze sword + bronze shield | Staff                  |
| To-hit bonus     | +3                           | +5                     |
| Damage           | 1d6 + 1                      | 1d6 + 2 (Fire bolt)    |
| Starting potions | 2                            | 0                      |
| Heal casts       | none                         | 1 (see _Game Balance_) |
| Starting gold    | 10                           | 10                     |
| Starting items   | Sword, shield, potions       | Staff                  |

There is no Armor Class: the player's defense is only the shield's damage absorption. The Mage has no defense at all. Only enemy attacks (including the serpent) are reduced by the shield; trap damage is not.

Inventory Rules:

- The bronze sword has one (1) additional damage point when the enemy is hit.
- The steel sword has three (3) additional damage points when the enemy is hit.
- Drinking a single potion adds eight (8) health points to the player.
- The bronze shield has a max durability of 6 and it starts with that.
- The bronze shield subtracts two (2) health points from any damage inflicted on the player from any enemy.
- The steel shield has a max durability of 10 and it starts with that.
- The steel shield subtracts four (4) health points from any damage inflicted on the player from any enemy.
- Either type of shield can be good, damaged, or broken. It is good if its durability multiplied by 2 is greater than its max durability. It is broken if its durability is zero or less. If it isn't good or broken, then it is damaged.
- When an enemy hits the player, the shield absorbs an amount and the player takes the rest. A "good" shield absorbs its full block value, a "damaged" shield half (minimum 1), and a "broken" shield 0. The amount absorbed is also capped by the shield's remaining durability and by the damage of the hit itself, so a shield never absorbs more than the blow deals. The shield loses one durability point per point absorbed; a hit that is fully absorbed does no damage, and a hit that is not absorbed at all costs the shield nothing.
- The Warrior has no damage bonus of its own; the sword supplies it, giving 1d6 + 1 with the bronze sword and 1d6 + 3 with the steel sword.

**Shop upgrades** (class-specific, so each class is only offered relevant gear):

- Warrior: **Steel Sword** (+2 damage over the bronze sword, so 1d6 + 3), **Steel Shield** (a sturdier shield, see _Combat_), **Potion** (+8 HP, usable anytime)
- Mage: **Elder Staff** (+3 damage over the staff, so 1d6 + 5)

**Which class can be played.** Both classes exist in the game logic, but the Gradio UI can currently only start a Warrior game; choosing the Mage is not yet supported there.

### What the Player Does

At the start, the player picks a class (Warrior or Mage) and is dropped into the Cave Entrance. From there, each turn follows the same loop:

1. The DM describes the current scene.
2. The player types what they want to do, in plain English (e.g. "I attack the goblin," "I buy a potion," "I go left").
3. The game figures out what kind of action that is (fighting, shopping, talking, exploring) and resolves it — rolling dice where the outcome is uncertain.
4. The DM narrates the result, and the player's HP / inventory / gold sidebar updates to match.

The player can type anything, but each turn resolves a **single action**. A compound command (e.g. "drink a potion and attack the troll") is rejected: the game replies "You can only perform one action at a time." and nothing happens. A command that matches nothing sensible, or isn't a legal intent in the current room, is narrated as not making sense or not possible here, again at no cost. Left and right are valid only in the Cave Chamber; everywhere else the only valid move is forward. The actions the game recognizes are: look, move (left / right / forward), attack (for the Mage this includes casting Fire bolt), buy, drink a potion (Warrior), cast Heal (Mage), and open a chest. Naming a weapon the player doesn't carry cancels the attack. Keeps combat math and the graph's logic simple, one action in, one resolved turn out.

- drinking a potion or casting Heal (including when none are left, so the action is refused),
- trying to leave the room (the Monster Room, the Throne Room, or the Treasure Room with the serpent loose),
- trying to open a chest in the Treasure Room while the serpent is loose (the other chest, or no chest named),
- any other legal intent that fails, such as moving in a wrong direction.

The commands that do not provoke a counterattack are looking around, compound ("multiple") or confused ("unknown") commands, and any intent that is illegal in the room (for example trying to buy or open a chest mid-fight): those are refused outright and nothing else happens. One full player turn — action, outcome, enemy counterattack, outcome — is resolved and narrated together as a single response. If the player dies from the counterattack, the game ends; if the enemy dies, the fight is over and no counterattack happens.

**The shield (Warrior).** The shield's absorption rules are defined under _Inventory Rules_ above; this is a summary. A shield cannot be repaired; it changes condition as it wears:

| Condition | When                                   | Absorbs from each blow            |
| --------- | -------------------------------------- | --------------------------------- |
| Good      | more than half durability left         | its full block value              |
| Damaged   | half durability or less, but some left | half its block value (at least 1) |
| Broken    | no durability left                     | nothing                           |

The bronze shield has block value 2 and durability 6; the steel shield has block value 4 and durability 10. The narration mentions when the shield becomes damaged or breaks.

### Game Balance

**Design goal:** the game should be fun, so a reasonably sensible player should win roughly **60–70% of runs or more**, yet losing must stay a real possibility, mostly in the Throne Room or after a bad streak in the challenge rooms. Dice add drama; the numbers below make sure the odds stay in the player's favor. All values are starting points to be validated by play-testing.

**Healing.** A potion restores 8 HP (never above the maximum); the Heal spell restores the Mage to full HP and is limited to a fixed number of casts: 1 with the starting staff, and buying the Elder staff adds 2 more on top of any casts left. Either takes the player's whole turn, so during a fight the enemy still counterattacks, which makes healing a real decision, not a free action. Outside a fight there is no counterattack. A potion drunk at full HP is used up for nothing, and a Heal cast at full HP still uses up a cast. When the player has no potions or Heal casts left, the action is refused (during a fight the enemy still counterattacks). Players start with enough healing to survive one bad fight, and the shop lets them prepare for the troll. Heal's small cast limit stops the Mage from out-sustaining everything.

**Enemies** (to-hit is added to the d20 and the total must reach 12; the player's shield then reduces the damage):

| Enemy     | HP  | Weapon             | To-hit | Damage | Notes                          |
| --------- | --- | ------------------ | ------ | ------ | ------------------------------ |
| Giant rat | 7   | Razor sharp teeth  | +2     | 1d3    | Easy warm-up                   |
| Goblin    | 10  | Dagger             | +3     | 1d4+1  | Average                        |
| Orc       | 16  | Battle ax          | +4     | 1d6+1  | Toughest of the monster room   |
| Serpent   | 12  | Fangs              | +3     | 1d6    | Ambush; no gold reward         |
| Troll     | 25  | Spiked wooden club | +4     | 1d8+2  | Hits for 3–10; avg 6.5 per hit |

**Resulting odds.** With a flat target of 12, a hit lands with probability (9 + to-hit bonus) / 20. The Warrior (+3) hits 60% of the time and the Mage (+5) 70%. The rat hits 55%, the goblin and serpent 60%, and the orc and troll 65%. The shield trims every hit: a good bronze shield absorbs up to 2 points, a good steel shield up to 4, which matters most against the many small hits of the monster rooms and takes a real bite out of the troll's 3–10. The Mage has no such protection. The troll fight lasts roughly 5–7 turns, so a player who arrives with 20+ HP and a healing option usually wins, while one who skipped the shop or ignored low HP can lose.

**Economy.** Gold sources: starting gold (10), Monster Room (5), Trap Room (4–6), Treasure Room gold chest (3–6, no gold from the serpent chest). Both classes start with 10 gold and reach the shop with 14–22. The Warrior can afford a steel sword or shield plus a potion or two; the Mage can afford the Elder Staff (15) in all but the unluckiest case (Trap Room with a 4-gold roll plus a serpent chest leaves 14 gold), a mild setback rather than a dead end.

**Win rates.** The earlier simulation figures (~75% Warrior, ~70% Mage) were computed with an Armor Class model that no longer matches the combat rules, so they should be treated as stale. Re-run the simulation against the current rules whenever the numbers change.

### Winning and Losing

- **Lose:** the player's HP reaches 0 at any point (in a fight or from the trap) — the game ends immediately with a death narration followed by a brief farewell.
- **Win:** the player defeats the troll in the Throne Room (its HP reaches 0) and reclaims the **Amulet of Valdorin** automatically — the narration tells them they have taken it from the troll's neck. The amulet's power then brings the player back to the kingdom, ending the run with a victory narration. Once the game is over, further commands are ignored.

### Session Length

A full playthrough — Cave Entrance through the troll fight — is designed to take roughly **5 to 15 minutes**, short enough to finish in one sitting while still passing through exploration, a random encounter or trap, a shop stop, and a final fight.

---

## Part 2 — Implementation (High Level)

### Tech Stack

- **LangGraph** — the state machine that drives the game: nodes for each type of turn, conditional edges for branching (fighting vs. not, alive vs. dead).
- **LangChain** — underlying building blocks used inside the graph: the chat model wrapper and structured output. Two agents are built on it: a **Router agent** that classifies the player's text into an intent, and a **Dungeon Master agent** that narrates results. The model is chosen with the `MODEL` environment variable (default `gpt-4o-mini`; a bare name means OpenAI, `provider:name` is used as given).
- **Gradio** — the chat-style UI, meant for deployment as a Hugging Face Space, with a status panel showing HP, shield condition, potions and gold, plus the current enemy's HP. The home page lets the player pick a hero; the game page shows the narration and takes commands.
- **Pydantic** — all game state (player, dungeon, rooms, merchant) is made of immutable-style models: nodes return updated copies rather than mutating state.

### Design Principle: Data vs. Narration

The dungeon's rooms, enemies, stats, and the merchant's stock are all defined as fixed data (Python/Pydantic models), not invented by the LLM. Graph nodes read and update this data directly — rolling the dice and checking real numbers like enemy HP — while the LLM's only job is to turn the outcome into narration. Each room supplies a list of "room facts" that the Dungeon Master is told to stick to, and each room declares its set of legal intents and validates whether the player's intent makes sense there (returning an instruction for how to narrate a refusal). An intent outside the set is refused before any node acts. This keeps the conditional edges reliable and the game state consistent across turns.

### The Workflow Graph

Each player command triggers exactly one graph invocation — input goes in, flows through the relevant nodes, and the narration comes out. The graph looks like this:

1. **Router Node** — asks the Router agent to classify the player's free-text input as explore, look, attack, shop, drink potion, cast healing, open chest, multiple, or unknown (only the intents the class supports are offered), and fills in details such as direction, chest side, shop item and quantity.
2. **Explore Node** — validates the move against the room and, if allowed, advances the player to the next room, marking the player as fighting when the room is a Monster Room or Throne Room. A forward move in an un-sprung Trap Room goes to the Cross Trap Node instead. During a fight, a refused move (leaving a Monster Room, Throne Room, or a Treasure Room with the serpent loose) goes on to the Enemy Attack Node, like every other command except look, multiple, and unknown.
3. **Cross Trap Node** — rolls the trap, applies any wound, awards the gold, then goes to the Game Over Node.
4. **Look Node** — describes the room; valid everywhere.
5. **Player Attack Node** — validates the attack, then rolls to hit and damage. If the enemy survives, it goes on to the Enemy Attack Node; if the troll died, it goes straight to the Game Over Node; if another enemy died, the turn ends (the player collects any gold).
6. **Enemy Attack Node** — the mirror image of the player's attack, applying the shield's absorption for the Warrior; then goes to the Game Over Node.
7. **Shop Node** — checks the merchant's stock and the player's gold; if the purchase is valid, hands the item to the player, deducts the gold, and reduces the merchant's stock.
8. **Drink Potion / Cast Healing Nodes** — heal the player; if the player is fighting, the Enemy Attack Node follows.
9. **Open Chest Node** — gives the gold or releases the serpent (and starts the fight).
10. **Game Over Node** — reached after the trap and after enemy attacks, or directly when the troll dies. It ends the game with a death or victory narration if the player's HP is 0 or the troll is dead; otherwise it does nothing.
11. **Multiple / Unknown / Illegal** — canned or narrated refusals for compound, nonsensical, or room-illegal commands. None of these goes on to the Enemy Attack Node.

**Example — an attack turn:** a player attack that wounds the enemy runs `Router → Player Attack → Enemy Attack → Game Over Node` (the last one only acts if the player just died). A killing blow on a monster is `Router → Player Attack`; a killing blow on the troll is `Router → Player Attack → Game Over`. Most other turns are just `Router → one node`.

### State and Persistence

The whole game is one `GameState` (player, dungeon, last command, intent, narration, and a game-over flag). Each Gradio session holds its own `GameState` and a log of the story so far in memory, and each command is run through the graph against that state. There is currently no checkpointer or database: closing the tab or restarting the server loses the game. Saving progress with LangGraph's checkpointer (keyed by `thread_id`) is a possible future addition.
