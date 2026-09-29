from collections.abc import Callable

from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call
from langchain.agents.structured_output import StructuredOutputError
from pydantic import BaseModel, Field

from dungeon_game.domain.intent import ActionType, ExploreOption


class RouterState(BaseModel):
    action: ActionType = Field(description="Action")
    explore_option: ExploreOption | None = Field(
        default=None,
        description="Which direction the player wants to move or if they are just looking around.",
    )


@wrap_model_call
def retry_on_invalid_structured_output(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    """Guardrail: retry a model call that returns malformed structured output.

    Small models occasionally hallucinate invalid tool-call arguments for
    optional Literal fields (e.g. echoing back the field's JSON schema
    instead of a real value), which raises StructuredOutputError. Retrying
    gives the model another chance to produce a valid response before we
    give up on the whole turn.
    """
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            return handler(request)
        except StructuredOutputError:
            if attempt == max_attempts - 1:
                raise


def create_router_agent(model: str):
    return create_agent(
        model=model,
        system_prompt="You are great at categorizing commands from the player.",
        response_format=RouterState,
        middleware=[retry_on_invalid_structured_output],
    )
