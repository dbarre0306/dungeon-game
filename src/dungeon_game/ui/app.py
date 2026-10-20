"""Gradio app assembly and launch."""

import gradio as gr

from dungeon_game.ui.content import TITLE
from dungeon_game.ui.home import build_home
from dungeon_game.ui.theme import CSS, THEME


def build_app() -> gr.Blocks:
    with gr.Blocks(title=TITLE) as demo:
        build_home()
    return demo


demo = build_app()


def launch() -> None:
    demo.launch(theme=THEME, css=CSS)
