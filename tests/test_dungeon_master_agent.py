from types import SimpleNamespace

from dungeon_game.agents.dungeon_master_agent import DungeonMasterAgent, DungeonMasterResponse
from dungeon_game.domain.actors.enemy import Enemy
from dungeon_game.domain.rooms.monster_room import MonsterRoom


class FakeAgent:
    def __init__(self):
        self.prompts: list[str] = []

    def invoke(self, user_msg):
        self.prompts.append(user_msg["messages"][0]["content"])
        return {"structured_response": DungeonMasterResponse(narration="narrated")}


def _agent_with_fake() -> tuple[DungeonMasterAgent, FakeAgent]:
    agent = object.__new__(DungeonMasterAgent)  # skip building the real LLM agent
    fake = FakeAgent()
    agent._agent = fake
    return agent, fake


def _room() -> MonsterRoom:
    enemy = Enemy(name="rat", weapon="teeth", max_health_points=10, health_points=10, hit_bonus=0)
    return MonsterRoom(enemy)


def test_prompt_includes_the_players_current_facts_on_every_call():
    agent, fake = _agent_with_fake()
    bronze = SimpleNamespace(get_facts=lambda: "The player has a bronze sword.")
    steel = SimpleNamespace(get_facts=lambda: "The player has a steel sword.")

    agent.invoke(_room(), bronze, "first")
    agent.invoke(_room(), steel, "second")

    assert "The player has a bronze sword." in fake.prompts[0]
    assert "The player has a steel sword." in fake.prompts[1]
    assert "bronze" not in fake.prompts[1]
