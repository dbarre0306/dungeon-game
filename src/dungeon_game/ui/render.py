"""Turn game state into the HTML shown beside and inside the narration."""

from html import escape

from dungeon_game.domain.actors.player.mage import Mage
from dungeon_game.domain.actors.player.player import Player
from dungeon_game.domain.actors.player.warrior import Warrior
from dungeon_game.game_state import GameState
from dungeon_game.ui.session import LogEntry

SHIELD_LABELS = {"good": "Good", "damaged": "Damaged", "broken": "Broken"}


def _bar(value: int, maximum: int, tone: str) -> str:
    percent = 0 if maximum <= 0 else max(0, min(100, round(100 * value / maximum)))
    return (
        f'<div class="mw-bar {tone}" role="meter" aria-valuemin="0" '
        f'aria-valuemax="{maximum}" aria-valuenow="{value}">'
        f'<span style="width:{percent}%"></span></div>'
    )


def _health_tone(value: int, maximum: int) -> str:
    if value * 4 <= maximum:
        return "low"
    if value * 2 <= maximum:
        return "hurt"
    return "good"


def _pips(filled: int, total: int) -> str:
    return "".join(
        f'<i class="{"on" if n < filled else "off"}"></i>' for n in range(total)
    )


def _row(label: str, value: str) -> str:
    return f"<dt>{label}</dt><dd>{value}</dd>"


def _enemy_html(state: GameState) -> str:
    enemy = getattr(state.get_current_room(), "enemy", None)
    if enemy is None or not state.player.is_fighting or enemy.is_dead():
        return ""
    tone = _health_tone(enemy.health_points, enemy.max_health_points)
    return (
        '<section class="mw-panel foe">'
        f'<p class="mw-label">Fighting</p>'
        '<div class="mw-foe-head">'
        f'<h3 class="mw-foe-name">{escape(enemy.name.capitalize())}</h3>'
        f'<p class="mw-foe-hp">{enemy.health_points}/{enemy.max_health_points} '
        "Health Points</p></div>"
        f"{_bar(enemy.health_points, enemy.max_health_points, tone)}"
        "</section>"
    )


def _health_html(player: Player) -> str:
    tone = _health_tone(player.health_points, player.max_health_points)
    return (
        '<section class="mw-panel">'
        '<p class="mw-vital">Health Points: '
        f"<strong>{player.health_points}/{player.max_health_points}</strong></p>"
        + _bar(player.health_points, player.max_health_points, tone)
        + "</section>"
    )


def _gear_html(rows: list[str]) -> str:
    return (
        '<section class="mw-panel"><dl class="mw-gear">'
        + "".join(rows)
        + "</dl></section>"
    )


def _warrior_rows(player: Warrior) -> list[str]:
    shield = player.shield
    condition = shield.condition
    return [
        _row("Weapon", escape(player.sword.name.capitalize())),
        _row(
            "Shield",
            f"{escape(shield.name.capitalize())}"
            f'<span class="mw-cond {condition}">{SHIELD_LABELS[condition]}</span>'
            f'<span class="mw-pips" title="Shield durability">'
            f"{_pips(shield.durability, shield.max_durability)}</span>",
        ),
        _row("Potions", str(player.potions.quantity)),
        _row("Gold coins", str(player.gold_coins)),
    ]


def _mage_rows(player: Mage) -> list[str]:
    return [
        _row("Weapon", escape(player.staff.name.capitalize())),
        _row("Heal casts", str(player.healing_casts_left)),
        _row("Gold coins", str(player.gold_coins)),
    ]


def hud_html(state: GameState) -> str:
    """The hero's vital signs and gear, and any foe being fought."""
    player = state.player
    if isinstance(player, Warrior):
        rows = _warrior_rows(player)
    elif isinstance(player, Mage):
        rows = _mage_rows(player)
    else:
        raise TypeError(f"The game screen does not support {type(player).__name__}")
    return (
        f'<aside class="mw-hud {player.type}">'
        + _health_html(player)
        + _gear_html(rows)
        + _enemy_html(state)
        + "</aside>"
    )


def _paragraphs(text: str) -> str:
    return escape(text).replace("\n", "<br>")


def _entry_html(entry: LogEntry) -> str:
    text = _paragraphs(entry.text)
    if entry.kind == "command":
        return f'<p class="mw-cmd">{text}</p>'
    if entry.kind == "error":
        return f'<p class="mw-err" role="alert">{text}</p>'
    return f'<p class="mw-narr">{text}</p>'


def log_html(log: list[LogEntry], *, waiting: bool, outcome: str | None) -> str:
    """The story so far, with the narrator's pending reply and any ending."""
    parts = [_entry_html(entry) for entry in log]
    if waiting:
        parts.append(
            '<p class="mw-wait" role="status" aria-label="The narrator is writing">'
            "<span></span><span></span><span></span></p>"
        )
    if outcome:
        parts.append(f'<p class="mw-outcome {outcome}">{OUTCOMES[outcome]}</p>')
    return (
        '<div class="mw-log" tabindex="0" aria-label="Story so far">'
        f'<div class="mw-log-inner">{"".join(parts)}</div></div>'
    )


OUTCOMES = {
    "victory": "The troll is slain and the Amulet of Valdorin is yours.",
    "defeat": "You have fallen. Your quest ends here.",
}


def outcome_of(state: GameState) -> str | None:
    if not state.game_over:
        return None
    return "defeat" if state.player.is_dead() else "victory"
