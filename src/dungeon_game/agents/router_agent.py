from collections.abc import Callable

from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call
from langchain.agents.structured_output import StructuredOutputError
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from dungeon_game.domain.intent import ActionType, ExploreDirection


class RouterState(BaseModel):
    action: ActionType = Field(description="Action")
    explore_direction: ExploreDirection | None = Field(
        default=None,
        description=(
            "Which direction the player wants to move "
            "or if they are just looking around."
        ),
    )


_MAX_ATTEMPTS = 3
_DIRECTION_HINT = (
    "When the action is explore, explore_direction must be one of: "
    "left, right, forward, backward. If you cannot tell which direction "
    "the player means, set the action to unknown."
)


def _is_explore_without_direction(response: ModelResponse) -> bool:
    router_state = response.structured_response
    return (
        router_state is not None
        and router_state.action == "explore"
        and router_state.explore_direction is None
    )


@wrap_model_call
def retry_on_invalid_router_output(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    """Guardrail: retry a model call that returns an unusable routing decision.

    Two failures are retried:

    - Malformed structured output. Small models occasionally hallucinate
      invalid tool-call arguments for optional Literal fields (e.g. echoing
      back the field's JSON schema instead of a real value), which raises
      StructuredOutputError. Once retries are exhausted the error is raised.
    - An explore action with no direction. Retries include a hint listing the
      valid directions. Once retries are exhausted the action is downgraded to
      unknown, so an explore that reaches the game always has a direction.
    """
    for attempt in range(_MAX_ATTEMPTS):
        is_last_attempt = attempt == _MAX_ATTEMPTS - 1
        try:
            response = handler(request)
        except StructuredOutputError:
            if is_last_attempt:
                raise
            continue
        if not _is_explore_without_direction(response):
            return response
        if is_last_attempt:
            return ModelResponse(
                result=response.result,
                structured_response=RouterState(action="unknown"),
            )
        request = request.override(
            messages=[*request.messages, HumanMessage(content=_DIRECTION_HINT)]
        )
    raise AssertionError("unreachable")  # pragma: no cover


class RouterAgent:
    def __init__(self, model):
        self._agent = create_agent(
            model=model,
            system_prompt="You are great at categorizing commands from the player.",
            response_format=RouterState,
            middleware=[retry_on_invalid_router_output],
        )

    def invoke(self, msg: str) -> RouterState:
        try:
            result = self._agent.invoke(
                {"messages": [{"role": "user", "content": msg}]}
            )
            return result["structured_response"]
        except StructuredOutputError:
            # The model occasionally returns malformed structured output
            # (e.g. for typos or ambiguous commands). Treat it as unknown
            # rather than crashing the whole game loop.
            return RouterState(action="unknown", explore_direction=None)
