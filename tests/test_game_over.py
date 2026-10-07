from types import SimpleNamespace

from dungeon_game.domain.actors.enemy import Enemy
from dungeon_game.domain.actors.player.warrior import create_default_warrior
from dungeon_game.domain.dungeon.dungeon import Dungeon
from dungeon_game.domain.rooms.monster_room import MonsterRoom
from dungeon_game.game_state import GameState
from dungeon_game.nodes.game_over import GameOverNode


class FakeDungeonMaster:
    def __init__(self):
        self.messages: list[str] = []

    def invoke(self, room, player, msg):
        self.messages.append(msg)
        return SimpleNamespace(narration="farewell")


def _state(player_hp: int) -> GameState:
    enemy = Enemy(
        name="goblin",
        weapon="dagger",
        max_health_points=10,
        health_points=5,
        hit_bonus=2,
    )
    player = create_default_warrior().model_copy(update={"health_points": player_hp})
    return GameState(
        player=player,
        dungeon=Dungeon(rooms=[MonsterRoom(enemy)]),
        command="attack",
        narration=["the goblin struck"],
    )


def test_living_player_continues_game():
    dm = FakeDungeonMaster()
    assert GameOverNode(dm).execute(_state(player_hp=5)) == {}
    assert dm.messages == []


def test_dead_player_ends_game_with_farewell_appended():
    dm = FakeDungeonMaster()
    update = GameOverNode(dm).execute(_state(player_hp=0))
    assert update["game_over"] is True
    assert update["narration"] == ["the goblin struck", "farewell"]
    assert len(dm.messages) == 1
