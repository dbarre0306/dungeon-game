"""Game page: the hero's status, the narration, and the command box."""

from dataclasses import dataclass

import gradio as gr

from dungeon_game.ui.content import TITLE
from dungeon_game.ui.render import hud_html, log_html, outcome_of
from dungeon_game.ui.session import (
    Session,
    queue_command,
    resolve_pending,
    start_session,
)

FOCUS_COMMAND_BOX = """() => setTimeout(
    () => document.querySelector('.mw-command input, .mw-command textarea')
        ?.focus(),
    100
)"""


@dataclass
class GameView:
    root: gr.Column
    hud: gr.HTML
    log: gr.HTML
    command: gr.Textbox
    act: gr.Button
    leave: gr.Button
    confirm: gr.Row
    confirm_leave: gr.Button
    stay: gr.Button


def build_game() -> GameView:
    """Render the (initially hidden) game page into the current Blocks context."""
    with gr.Column(visible=False, elem_classes="mw-game") as root:
        with gr.Row(elem_classes="mw-topbar"):
            gr.HTML(f'<p class="mw-brand">{TITLE}</p>')
            leave = gr.Button("Leave the dungeon", elem_classes="mw-leave", scale=0)
        with gr.Row(visible=False, elem_classes="mw-confirm") as confirm:
            gr.HTML(
                '<p class="mw-confirm-text">Leave the dungeon? '
                "Your game will be lost.</p>"
            )
            stay = gr.Button("Keep playing", elem_classes="mw-stay", scale=0)
            confirm_leave = gr.Button("Leave", elem_classes="mw-leave-now", scale=0)
        with gr.Row(elem_classes="mw-board"):
            with gr.Column(scale=1, min_width=260):
                hud = gr.HTML()
            with gr.Column(scale=2, min_width=320):
                log = gr.HTML()
                with gr.Row(elem_classes="mw-input-row"):
                    command = gr.Textbox(
                        placeholder="What do you do?",
                        show_label=False,
                        container=False,
                        lines=1,
                        max_lines=1,
                        scale=1,
                        elem_classes="mw-command",
                    )
                    act = gr.Button(
                        "Act", variant="primary", scale=0, elem_classes="mw-act"
                    )
    return GameView(root, hud, log, command, act, leave, confirm, confirm_leave, stay)


def _render(session: Session) -> tuple[str, str]:
    waiting = session.pending is not None
    outcome = outcome_of(session.state)
    return (
        hud_html(session.state),
        log_html(session.log, waiting=waiting, outcome=outcome),
    )


def wire_game(
    home: gr.Column,
    play_warrior: gr.Button,
    game: GameView,
    session: gr.State,
) -> None:
    """Connect the Warrior's play button and the game page's controls."""
    views = [home, game.root]

    def enter_game():
        new_session = start_session("warrior")
        hud, log = _render(new_session)
        return (
            new_session,
            gr.update(visible=False),
            gr.update(visible=True),
            hud,
            log,
            gr.update(value="", interactive=False),
        )

    def submit(current: Session | None, text: str):
        if current is None:
            return gr.skip(), gr.skip(), gr.skip(), gr.skip()
        current = queue_command(current, text)
        hud, log = _render(current)
        return current, hud, log, gr.update(value="", interactive=False)

    def resolve(current: Session | None):
        if current is None:
            return gr.skip(), gr.skip(), gr.skip(), gr.skip()
        current = resolve_pending(current)
        hud, log = _render(current)
        return current, hud, log, gr.update(interactive=not current.state.game_over)

    def ask_to_leave():
        return gr.update(visible=False), gr.update(visible=True)

    def keep_playing():
        return gr.update(visible=True), gr.update(visible=False)

    def leave_game():
        return (
            None,
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False),
        )

    turn_outputs = [session, game.hud, game.log, game.command]

    play_warrior.click(
        enter_game,
        outputs=[session, *views, game.hud, game.log, game.command],
    ).then(resolve, session, turn_outputs).then(None, js=FOCUS_COMMAND_BOX)

    for trigger in (game.command.submit, game.act.click):
        trigger(
            submit, [session, game.command], turn_outputs, show_progress="hidden"
        ).then(resolve, session, turn_outputs, show_progress="hidden").then(
            None, js=FOCUS_COMMAND_BOX
        )

    ask_outputs = [game.leave, game.confirm]
    game.leave.click(ask_to_leave, outputs=ask_outputs)
    game.stay.click(keep_playing, outputs=ask_outputs)
    game.confirm_leave.click(leave_game, outputs=[session, *views, *ask_outputs])
