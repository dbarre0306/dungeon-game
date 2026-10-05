from types import SimpleNamespace

from dungeon_game.domain.dungeon.dungeon import Dungeon
from dungeon_game.domain.npc.enemy import Enemy
from dungeon_game.domain.player.warrior import create_default_warrior
from dungeon_game.domain.rooms.monster_room import MonsterRoom
from dungeon_game.game_state import GameState
from dungeon_game.nodes.enemy_attack import EnemyAttackNode


class FakeDice:
    def __init__(self, *rolls: int):
        self._rolls = list(rolls)

    def roll(self, num_sides: int) -> int:
        return self._rolls.pop(0)


class FakeDungeonMaster:
    def __init__(self):
        self.messages: list[str] = []

    def invoke(self, room, msg):
        self.messages.append(msg)
        return SimpleNamespace(narration="narrated")


def _state(player_hp: int = 20, enemy_hp: int = 5) -> GameState:
    enemy = Enemy(
        name="goblin", description="goblin", health_points=enemy_hp, hit_bonus=2, damage_bonus=1
    )
    player = create_default_warrior().model_copy(
        update={"health_points": player_hp, "is_fighting": True}
    )
    return GameState(player=player, dungeon=Dungeon(rooms=[MonsterRoom(enemy)]), command="attack")


def _execute(state: GameState, *rolls: int):
    dm = FakeDungeonMaster()
    return EnemyAttackNode(dm, FakeDice(*rolls)).execute(state), dm


def test_miss_leaves_player_unharmed():
    update, dm = _execute(_state(), 1)
    assert update["player"].health_points == 20
    assert update["player"].is_fighting
    assert "missed" in dm.messages[0]


def test_hit_applies_damage_minus_shield():
    # d20=20 hits; d6=6 + damage_bonus 1 - shield 2 = 5
    update, _ = _execute(_state(), 20, 6)
    assert update["player"].health_points == 15
    assert update["player"].is_fighting
    assert update["dungeon"].rooms[0].history == ["narrated"]


def test_narration_is_appended_to_existing_narration():
    state = _state().model_copy(update={"narration": ["You swing your sword."]})
    update, _ = _execute(state, 1)
    assert update["narration"] == ["You swing your sword.", "narrated"]


def test_hit_always_does_at_least_one_damage():
    update, _ = _execute(_state(), 20, 1)
    assert update["player"].health_points == 19


def test_killing_blow_ends_the_fight():
    update, dm = _execute(_state(player_hp=3), 20, 6)
    assert update["player"].health_points == 0
    assert update["player"].is_dead()
    assert not update["player"].is_fighting
    assert "killed the player" in dm.messages[0]


def test_dead_enemy_does_not_attack():
    update, dm = _execute(_state(enemy_hp=0))
    assert update == {}
    assert dm.messages == []
