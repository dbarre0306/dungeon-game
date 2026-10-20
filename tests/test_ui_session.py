from dungeon_game.game_state import GameState
from dungeon_game.ui.render import hud_html, log_html, outcome_of
from dungeon_game.ui.session import (
    ERROR_MESSAGE,
    LogEntry,
    queue_command,
    resolve_pending,
    start_session,
)


class FakeGraph:
    def __init__(self, narration: list[str] | None = None, fail: bool = False):
        self.narration = narration or []
        self.fail = fail
        self.commands: list[str] = []

    def invoke(self, state: GameState) -> GameState:
        self.commands.append(state.command)
        if self.fail:
            raise RuntimeError("secret-key-123")
        return state.model_copy(update={"narration": self.narration})


def test_new_warrior_session_opens_the_scene_first():
    session = start_session("warrior")
    assert session.pending == "look around"
    assert session.state.player.type == "warrior"


def test_resolving_adds_narration_and_clears_pending():
    session = start_session("warrior")
    graph = FakeGraph(["You see a cave."])
    resolve_pending(session, graph)
    assert session.pending is None
    assert session.log == [LogEntry("narration", "You see a cave.")]
    assert graph.commands == ["look around"]


def test_queue_ignores_blank_input_and_turns_in_progress():
    session = start_session("warrior")
    resolve_pending(session, FakeGraph(["Hi."]))
    queue_command(session, "   ")
    assert session.pending is None
    queue_command(session, "attack")
    queue_command(session, "look")
    assert session.pending == "attack"
    assert [e.text for e in session.log if e.kind == "command"] == ["attack"]


def test_failed_turn_logs_a_generic_error_without_leaking_details():
    session = start_session("warrior")
    resolve_pending(session, FakeGraph(fail=True))
    assert session.log == [LogEntry("error", ERROR_MESSAGE)]
    assert "secret" not in ERROR_MESSAGE


def test_hud_shows_health_weapon_shield_potions_gold_and_room():
    html = hud_html(start_session("warrior").state)
    for expected in [
        "Cave entrance",
        "Room 1 of 6",
        "30",
        "Bronze sword",
        "Bronze shield",
        "Good",
        "Potions",
        "Gold coins",
    ]:
        assert expected in html
    assert "Fighting" not in html


def test_hud_reports_a_damaged_shield():
    state = start_session("warrior").state
    worn = state.player.with_defense_worn(4)
    html = hud_html(state.model_copy(update={"player": worn}))
    assert "Damaged" in html


def test_log_escapes_text_and_shows_waiting_and_outcome():
    html = log_html(
        [LogEntry("narration", "<script>x</script>")], waiting=True, outcome="defeat"
    )
    assert "<script>" not in html
    assert "mw-wait" in html
    assert "You have fallen" in html


def test_outcome_depends_on_game_over_and_health():
    state = start_session("warrior").state
    assert outcome_of(state) is None
    dead = state.model_copy(
        update={"player": state.player.with_damage(99), "game_over": True}
    )
    assert outcome_of(dead) == "defeat"
    assert outcome_of(state.model_copy(update={"game_over": True})) == "victory"
