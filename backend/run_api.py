import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))
from tarot_bkd.api import build_app
import uvicorn
app = build_app()
uvicorn.run(app, host="127.0.0.1", port=8000)
