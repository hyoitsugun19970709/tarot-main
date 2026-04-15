#!/bin/bash
cd "$(dirname "$0")"
export $(cat .env | xargs)
python3 -c "
import sys, pathlib, uvicorn
sys.path.insert(0, 'src')
from tarot_bkd.api import build_app
app = build_app()
uvicorn.run(app, host='0.0.0.0', port=8000)
"
