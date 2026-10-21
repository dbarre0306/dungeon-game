import sys
from pathlib import Path

# Hugging Face installs only requirements.txt, not the project itself.
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dungeon_game.ui import launch  # noqa: E402

if __name__ == "__main__":
    launch()
