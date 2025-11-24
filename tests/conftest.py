import sys
from pathlib import Path

# ensure project/src is on sys.path so "from domain.bingo_card import BingoCard" works
sys.path.insert(0, str((Path(__file__).resolve().parents[1] / "src").resolve()))