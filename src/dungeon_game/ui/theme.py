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

footer { display: none !important; }

@media (max-width: 640px) {
  .mw-card dl { grid-template-columns: 1fr; gap: 0; }
  .mw-card dd { margin-bottom: .5rem; }
}
"""

THEME = gr.themes.Base()
