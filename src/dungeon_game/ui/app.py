"""Gradio app assembly and launch."""

import gradio as gr

from dungeon_game.ui.content import TITLE
from dungeon_game.ui.game_view import build_game, wire_game
from dungeon_game.ui.home import build_home
from dungeon_game.ui.theme import CSS, THEME


def build_app() -> gr.Blocks:
    with gr.Blocks(title=TITLE) as demo:
        session = gr.State()
        with gr.Column(elem_classes="mw-home") as home:
            play_buttons = build_home()
        game = build_game()
        wire_game(home, play_buttons, game, session)
    return demo


demo = build_app()


def launch() -> None:
    # SSR (on by default on Hugging Face) leaves custom CSS unscoped, so Gradio's
    # own .prose rules override it.
    demo.launch(theme=THEME, css=CSS, ssr_mode=False)
