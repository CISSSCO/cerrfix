from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FIX_DIR = BASE_DIR / "fixes"

FIX_DIR.mkdir(exist_ok=True)

