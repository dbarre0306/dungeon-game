import os
import pprint
from typing import Literal, TypedDict

from dotenv import load_dotenv
from langchain.agents import create_agent
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

load_dotenv()


class GameState(TypedDict):
    location: str
    health_points: int
    player_type: Literal["warrior", "mage"]
    command: str
    action: Literal["explore", "combat", "unknown"]
    narration: str


class Instructions(BaseModel):
    text: str


class RouterState(BaseModel):
    # action: Literal["combat", "shop", "explore", "multiple", "unknown"] = Field(
    action: Literal["combat", "explore", "unknown"] = Field(description="The action")


class Game:

    def __init__(self):
        model = f"openai:{os.getenv("MODEL", "gpt-4o-mini")}"
        self.router_agent = create_agent(
            model=model,
            system_prompt="You are great at categorizing commands.",
            response_format=RouterState,
        )

        self.explore_agent = create_agent(
            model=model,
            system_prompt="You are great at exploring.",
        )

        self.combat_agent = create_agent(
            model=model,
            system_prompt="You are great at fighting.",
        )

    def router(self, state: GameState) -> GameState:
        result = self.router_agent.invoke(
            {"messages": [{"role": "user", "content": state["command"]}]}
        )
        return {"action": result["structured_response"].action}

    def explore(self, state: GameState) -> GameState:
        # self.explore_agent.invoke({"messages": [{"role": "user", "content": ""}]})
        return {"narration": "explore"}

    def combat(self, state: GameState) -> GameState:
        # self.combat_agent.invoke({"messages": [{"role": "user", "content": ""}]})
        return {"narration": "combat"}

    def unknown(self, state: GameState) -> GameState:
        return {"narration": "I don't understand what you are saying."}

    def next_action(self, state: GameState) -> Literal["explore", "combat", "unknown"]:
        return state["action"]

    def run(self) -> None:

        agent_builder = StateGraph(GameState)

        # Add nodes
        agent_builder.add_node("router", self.router)
        agent_builder.add_node("explore", self.explore)
        agent_builder.add_node("combat", self.combat)
        agent_builder.add_node("unknown", self.unknown)

        # Add edges to connect nodes
        agent_builder.add_edge(START, "router")
        agent_builder.add_conditional_edges(
            "router", self.next_action, ["explore", "combat", "unknown"]
        )
        agent_builder.add_edge("explore", END)
        agent_builder.add_edge("combat", END)
        agent_builder.add_edge("unknown", END)

        # Compile the agent
        agent = agent_builder.compile()

        command = input("> ")
        while command != "x":
            state = agent.invoke(
                {"command": command, "player_type": "warrior", "health_points": 10}
            )
            pprint.pprint(state)
            command = input("> ")
