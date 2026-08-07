from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from taskassigner.app import create_app
from taskassigner.db_init import ensure_schema


if __name__ == "__main__":
    app = create_app()
    ensure_schema(app)
    print("DB_INIT_OK")
