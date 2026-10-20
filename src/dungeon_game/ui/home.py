"""Home page: what the game is, how to play, and picking a class."""

import gradio as gr

from dungeon_game.ui.content import (
    ABOUT,
    CLASSES,
    HOW_TO_PLAY,
    QUEST,
    TITLE,
    PlayerClass,
)


def _intro_html() -> str:
    return (
        '<div class="mw-page"><div class="mw-intro">'
        f'<h1 class="mw-title">{TITLE}</h1>'
        f'<p class="mw-quest">{QUEST}</p>'
        f'<p class="mw-about">{ABOUT}</p>'
        '<h2 class="mw-heading">How to play</h2>'
        '<ol class="mw-steps">'
        + "".join(f"<li>{step}</li>" for step in HOW_TO_PLAY)
        + "</ol>"
        '<h2 class="mw-heading">Choose your hero</h2>'
        "</div></div>"
    )


def _card_html(player_class: PlayerClass) -> str:
    rows = "".join(
        f"<dt>{label}</dt><dd>{value}</dd>" for label, value in player_class.stats
    )
    return (
        f'<article class="mw-card {player_class.key}">'
        f"<h3>{player_class.name}</h3>"
        f'<p class="tagline">{player_class.tagline}</p>'
        f"<dl>{rows}</dl>"
        "</article>"
    )


def build_home() -> dict[str, gr.Button]:
    """Render the home page into the current Blocks context.

    Returns the play buttons keyed by class key so callers can attach behavior
    to them later.
    """
    gr.HTML(_intro_html())

    play_buttons: dict[str, gr.Button] = {}
    with gr.Row(elem_classes="mw-page mw-row"):
        for player_class in CLASSES:
            with gr.Column():
                gr.HTML(_card_html(player_class))
                play_buttons[player_class.key] = gr.Button(
                    f"Play as the {player_class.name}",
                    elem_classes=["mw-play", player_class.key],
                )

    return play_buttons
