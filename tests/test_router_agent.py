import pytest
from langchain.agents.middleware import ModelRequest, ModelResponse
from langchain.agents.structured_output import StructuredOutputError
from langchain_core.messages import AIMessage, HumanMessage

from dungeon_game.agents.router_agent import (
    RouterState,
    retry_on_invalid_router_output,
)


class _FakeHandler:
    def __init__(self, states: list[RouterState | StructuredOutputError]):
        self._states = list(states)
        self.requests: list[ModelRequest] = []

    def __call__(self, request: ModelRequest) -> ModelResponse:
        self.requests.append(request)
        state = self._states.pop(0)
        if isinstance(state, StructuredOutputError):
            raise state
        return ModelResponse(result=[AIMessage(content="")], structured_response=state)


def _request() -> ModelRequest:
    return ModelRequest(
        model=None,  # type: ignore[arg-type]
        messages=[HumanMessage(content="leave")],
    )


def _call(handler: _FakeHandler) -> ModelResponse:
    return retry_on_invalid_router_output.wrap_model_call(_request(), handler)


def test_valid_explore_is_not_retried():
    handler = _FakeHandler([RouterState(action="explore", explore_direction="left")])
    response = _call(handler)
    assert response.structured_response.explore_direction == "left"
    assert len(handler.requests) == 1


def test_non_explore_without_direction_is_not_retried():
    handler = _FakeHandler([RouterState(action="attack")])
    response = _call(handler)
    assert response.structured_response.action == "attack"
    assert len(handler.requests) == 1


def test_explore_without_direction_retries_with_hint():
    handler = _FakeHandler(
        [
            RouterState(action="explore"),
            RouterState(action="explore", explore_direction="forward"),
        ]
    )
    response = _call(handler)
    assert response.structured_response.explore_direction == "forward"
    assert len(handler.requests) == 2
    assert len(handler.requests[1].messages) == 2


def test_explore_without_direction_becomes_unknown_after_retries():
    handler = _FakeHandler([RouterState(action="explore")] * 3)
    response = _call(handler)
    assert response.structured_response.action == "unknown"
    assert response.structured_response.explore_direction is None
    assert len(handler.requests) == 3


def test_structured_output_error_is_retried():
    handler = _FakeHandler(
        [
            StructuredOutputError(),
            StructuredOutputError(),
            RouterState(action="attack"),
        ]
    )
    response = _call(handler)
    assert response.structured_response.action == "attack"
    assert len(handler.requests) == 3


def test_structured_output_error_is_raised_after_retries():
    handler = _FakeHandler([StructuredOutputError()] * 3)
    with pytest.raises(StructuredOutputError):
        _call(handler)
    assert len(handler.requests) == 3
