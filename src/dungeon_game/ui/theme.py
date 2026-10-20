# ruff: noqa: E501  (CSS lines are easier to read unwrapped)
"""Visual theme for the UI: a torchlit stone dungeon seen through fog."""

import gradio as gr

# Palette: fog-black ground, bone text, torch-ember for the Warrior,
# witch-light teal for the Mage.
CSS = """
@import url('https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&family=Spectral:wght@400;500;600&display=swap');

:root, .dark {
  --mw-ground: #0d1210;
  --mw-stone: #17201c;
  --mw-stone-edge: #2a3831;
  --mw-bone: #e8dfc8;
  --mw-mist: #93a69c;
  --mw-ember: #e0873a;
  --mw-witch: #6cc4bb;
  --mw-accent: var(--mw-mist);
  --body-background-fill: var(--mw-ground);
  --background-fill-primary: var(--mw-ground);
  --block-background-fill: transparent;
  --body-text-color: var(--mw-bone);
}

body, .gradio-container {
  background: var(--mw-ground) !important;
  color: var(--mw-bone);
  font-family: 'Spectral', Georgia, serif;
}

/* Fog drifting behind the page: the single ambient moment. */
.gradio-container::before {
  content: "";
  position: fixed;
  inset: -20% -10%;
  pointer-events: none;
  background:
    radial-gradient(ellipse 60% 40% at 20% 15%, rgba(147,166,156,.16), transparent 70%),
    radial-gradient(ellipse 50% 35% at 85% 60%, rgba(147,166,156,.10), transparent 70%);
  animation: mw-drift 40s ease-in-out infinite alternate;
}
@keyframes mw-drift {
  from { transform: translate3d(-3%, 0, 0); }
  to   { transform: translate3d(4%, 2%, 0); }
}
@media (prefers-reduced-motion: reduce) {
  .gradio-container::before { animation: none; }
}

.mw-page { max-width: 62rem; margin: 0 auto; padding: 1.5rem 16px 0; position: relative; }

/* The title sets the width of the intro column; the text below fills it. */
.mw-intro { width: fit-content; max-width: 100%; }
.mw-intro > :not(.mw-title) { width: 0; min-width: 100%; }

.mw-title {
  font-family: 'IM Fell English', Georgia, serif;
  font-weight: 400;
  font-size: clamp(2.8rem, 9vw, 6rem);
  line-height: 1;
  letter-spacing: -0.01em;
  margin: 0 0 .9rem;
  color: var(--mw-bone);
}
.mw-quest {
  font-size: clamp(1.15rem, 2.6vw, 1.5rem);
  line-height: 1.5;
  margin: 0 0 1rem;
  color: var(--mw-bone);
}
.mw-about { line-height: 1.6; color: var(--mw-mist); margin: 0; }

.mw-heading {
  font-family: 'IM Fell English', Georgia, serif;
  font-weight: 400;
  font-size: 1.9rem;
  margin: 1.75rem 0 .6rem;
  color: var(--mw-bone);
}

.mw-steps { padding-left: 1.4rem; line-height: 1.6; margin: 0 0 .6rem; }
.mw-steps li { margin-bottom: .3rem; padding-left: .3rem; }
.mw-steps li::marker { color: var(--mw-ember); font-family: 'IM Fell English', serif; }

/* The card row continues the intro column, so it drops the page's top padding. */
.mw-row { padding-top: 0; padding-bottom: 1.5rem; }
/* Gradio pads its HTML wrappers; remove it so cards align with the buttons. */
.mw-row .html-container, .mw-row .prose { padding: 0 !important; }
/* Let each card stretch to the height of the taller one in its row. */
.mw-row { align-items: stretch !important; }
.mw-row > .column > .block:has(.mw-card) { flex-grow: 1; }
.mw-row .block:has(.mw-card), .mw-row .html-container, .mw-row .prose {
  display: flex; flex-direction: column; flex: 1;
}

/* Class cards */
.mw-card {
  --mw-accent: var(--mw-mist);
  border: 1px solid var(--mw-stone-edge);
  background: var(--mw-stone);
  padding: 1.5rem 1.5rem 1.25rem;
  border-radius: 4px;
  flex: 1;
}
.mw-card.warrior { --mw-accent: var(--mw-ember); }
.mw-card.mage { --mw-accent: var(--mw-witch); }
.mw-card h3 {
  font-family: 'IM Fell English', Georgia, serif;
  font-weight: 400;
  font-size: 2.1rem;
  margin: 0 0 .25rem;
  color: var(--mw-accent);
}
.mw-card .tagline { margin: 0 0 1.1rem; font-style: italic; color: var(--mw-mist); }
.mw-card dl { margin: 0; display: grid; grid-template-columns: max-content 1fr; gap: .45rem 1.1rem; }
.mw-card dt { color: var(--mw-mist); }
.mw-card dd { margin: 0; }

/* Play buttons */
.mw-play {
  font-family: 'Spectral', Georgia, serif !important;
  font-size: 1.1rem !important;
  font-weight: 600 !important;
  border-radius: 4px !important;
  background: transparent !important;
  border: 1px solid var(--mw-mist) !important;
  color: var(--mw-bone) !important;
  box-shadow: none !important;
  padding: .8rem 1rem !important;
}
.mw-play.warrior:hover { background: var(--mw-ember) !important; border-color: var(--mw-ember) !important; color: #1a0f05 !important; }
.mw-play.mage:hover { background: var(--mw-witch) !important; border-color: var(--mw-witch) !important; color: #06201d !important; }
.mw-play:focus-visible {
  outline: 2px solid var(--mw-bone) !important;
  outline-offset: 3px;
}

/* Game page */
.mw-game { max-width: 72rem; margin: 0 auto; padding: 1rem 16px 2rem; position: relative; gap: .75rem; }
.mw-game .html-container, .mw-game .prose { padding: 0 !important; }
.mw-topbar { align-items: center !important; }
.mw-brand { font-family: 'IM Fell English', Georgia, serif; font-size: 1.6rem; margin: 0; color: var(--mw-mist); }
.mw-leave {
  background: transparent !important; border: 1px solid var(--mw-stone-edge) !important;
  color: var(--mw-mist) !important; box-shadow: none !important; border-radius: 4px !important;
  font-family: 'Spectral', Georgia, serif !important; flex: 0 0 auto !important; width: auto !important;
}
.mw-leave:hover { border-color: var(--mw-mist) !important; color: var(--mw-bone) !important; }
.mw-confirm { align-items: center !important; gap: .75rem; padding: .6rem 1rem; border: 1px solid #6b3a2e; border-radius: 4px; background: var(--mw-stone); }
.mw-confirm-text { margin: 0; color: var(--mw-bone); }
.mw-stay, .mw-leave-now {
  font-family: 'Spectral', Georgia, serif !important; border-radius: 4px !important; box-shadow: none !important;
  flex: 0 0 auto !important; width: auto !important;
}
.mw-stay { background: transparent !important; border: 1px solid var(--mw-mist) !important; color: var(--mw-bone) !important; }
.mw-stay:hover { background: var(--mw-mist) !important; color: var(--mw-ground) !important; }
.mw-leave-now { background: #c4503f !important; border: 1px solid #c4503f !important; color: #1a0805 !important; font-weight: 600 !important; }
.mw-stay:focus-visible, .mw-leave-now:focus-visible { outline: 2px solid var(--mw-bone) !important; outline-offset: 3px; }

.mw-board { align-items: flex-start !important; gap: 1rem; }

.mw-hud { --mw-accent: var(--mw-ember); display: flex; flex-direction: column; gap: .75rem; }
.mw-panel { border: 1px solid var(--mw-stone-edge); background: var(--mw-stone); border-radius: 4px; padding: 1rem 1.15rem; }
.mw-panel.foe { border-color: #6b3a2e; }
.mw-label { margin: 0 0 .2rem; color: var(--mw-mist); font-size: .95rem; font-style: italic; }
.mw-sub { margin: .45rem 0 0; color: var(--mw-mist); font-size: .95rem; }
.mw-room-name, .mw-foe-name {
  font-family: 'IM Fell English', Georgia, serif; font-weight: 400; font-size: 1.9rem;
  line-height: 1.1; margin: 0 0 .7rem; color: var(--mw-accent);
}
.mw-foe-head { display: flex; justify-content: space-between; align-items: baseline; gap: .75rem; margin-bottom: .5rem; }
.mw-foe-name { font-size: 1.5rem; margin: 0; }
.mw-foe-hp { margin: 0; color: var(--mw-mist); white-space: nowrap; }
.mw-trail { display: flex; gap: .35rem; }
.mw-trail i { flex: 1; height: 4px; border-radius: 2px; background: var(--mw-stone-edge); }
.mw-trail i.on { background: var(--mw-accent); }
.mw-vital { font-family: 'IM Fell English', Georgia, serif; font-size: 1.6rem; line-height: 1.2; margin: 0 0 .6rem; color: var(--mw-mist); }
.mw-vital strong { font-weight: 400; color: var(--mw-bone); }
.mw-bar { height: 10px; border-radius: 5px; background: var(--mw-ground); border: 1px solid var(--mw-stone-edge); overflow: hidden; }
.mw-bar span { display: block; height: 100%; transition: width .4s ease; }
.mw-bar.good span { background: #7fa66a; }
.mw-bar.hurt span { background: var(--mw-ember); }
.mw-bar.low span { background: #c4503f; }
.mw-gear { margin: 0; display: grid; grid-template-columns: max-content 1fr; gap: .6rem 1rem; align-items: baseline; }
.mw-gear dt { color: var(--mw-mist); }
.mw-gear dd { margin: 0; color: var(--mw-bone); }
.mw-cond { display: block; font-style: italic; font-size: .95rem; margin-top: .1rem; }
.mw-cond.good { color: #7fa66a; }
.mw-cond.damaged { color: var(--mw-ember); }
.mw-cond.broken { color: #c4503f; }
.mw-pips { display: flex; gap: 3px; margin-top: .35rem; }
.mw-pips i { width: 14px; height: 8px; border-radius: 1px; background: var(--mw-ground); border: 1px solid var(--mw-stone-edge); }
.mw-pips i.on { background: var(--mw-mist); border-color: var(--mw-mist); }

/* Narration: a flipped flex column keeps the newest text in view. */
.mw-log {
  display: flex; flex-direction: column-reverse; overflow-y: scroll; overscroll-behavior: contain;
  scrollbar-width: thin; scrollbar-color: var(--mw-mist) var(--mw-ground);
  height: min(58vh, 34rem); border: 1px solid var(--mw-stone-edge); border-radius: 4px;
  background: linear-gradient(180deg, #121a16, var(--mw-stone)); padding: 1.25rem 1.5rem;
}
.mw-log::-webkit-scrollbar { width: 10px; }
.mw-log::-webkit-scrollbar-track { background: var(--mw-ground); }
.mw-log::-webkit-scrollbar-thumb { background: var(--mw-mist); border-radius: 5px; border: 2px solid var(--mw-ground); }
.mw-log:focus-visible { outline: 2px solid var(--mw-mist); outline-offset: 2px; }
.mw-log-inner { display: block; }
.mw-log p { margin: 0 0 1rem; }
.mw-narr { font-size: 1.15rem; line-height: 1.65; color: var(--mw-bone); }
.mw-cmd { font-style: italic; color: var(--mw-ember); }
.mw-cmd::before { content: "› "; }
.mw-err { color: #e08a7a; border-left: 3px solid #c4503f; padding-left: .8rem; }
.mw-wait { display: flex; gap: .4rem; }
.mw-wait span { width: 7px; height: 7px; border-radius: 50%; background: var(--mw-mist); animation: mw-pulse 1.2s ease-in-out infinite; }
.mw-wait span:nth-child(2) { animation-delay: .2s; }
.mw-wait span:nth-child(3) { animation-delay: .4s; }
@keyframes mw-pulse { 0%, 100% { opacity: .25; } 50% { opacity: 1; } }
.mw-outcome { font-family: 'IM Fell English', Georgia, serif; font-size: 1.6rem; text-align: center; padding-top: .5rem; border-top: 1px solid var(--mw-stone-edge); }
.mw-outcome.victory { color: var(--mw-ember); }
.mw-outcome.defeat { color: #c4503f; }

.mw-input-row { align-items: stretch !important; gap: .5rem; }
.mw-command textarea, .mw-command input {
  background: var(--mw-stone) !important; color: var(--mw-bone) !important;
  border: 1px solid var(--mw-mist) !important; border-radius: 4px !important;
  font-family: 'Spectral', Georgia, serif !important; font-size: 1.1rem !important; padding: .8rem 1rem !important;
}
.mw-command textarea:focus { border-color: var(--mw-ember) !important; box-shadow: 0 0 0 1px var(--mw-ember) !important; }
.mw-command textarea:disabled { opacity: .5; }
.mw-act {
  background: var(--mw-ember) !important; border: 1px solid var(--mw-ember) !important; color: #1a0f05 !important;
  font-family: 'Spectral', Georgia, serif !important; font-weight: 600 !important; font-size: 1.1rem !important;
  border-radius: 4px !important; box-shadow: none !important; flex: 0 0 auto !important; width: auto !important; padding: 0 1.6rem !important;
}
.mw-act:focus-visible, .mw-leave:focus-visible { outline: 2px solid var(--mw-bone) !important; outline-offset: 3px; }
@media (prefers-reduced-motion: reduce) {
  .mw-wait span { animation: none; opacity: .7; }
  .mw-bar span { transition: none; }
}

footer { display: none !important; }

@media (max-width: 640px) {
  .mw-card dl { grid-template-columns: 1fr; gap: 0; }
  .mw-card dd { margin-bottom: .5rem; }
}
"""

THEME = gr.themes.Base()
