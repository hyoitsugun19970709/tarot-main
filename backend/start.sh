#!/bin/bash
cd /Users/hyo.itsugun/.openclaw/workspace/tarot-main/backend
python3 -c "
import sys, pathlib, uvicorn
sys.path.insert(0, 'src')
from tarot_bkd.api import build_app
app = build_app()
uvicorn.run(app, host='127.0.0.1', port=8000)
"
