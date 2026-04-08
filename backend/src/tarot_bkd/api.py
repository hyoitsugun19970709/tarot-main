from __future__ import annotations

import json
import sys
import pathlib
import threading
from typing import Literal
from uuid import uuid4
from datetime import datetime
from typing import Any, Callable
from dataclasses import dataclass, field

# Add src to path so tarot_bkd can be imported when running from backend/
_backend_root = pathlib.Path(__file__).resolve().parent.parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from pydantic import BaseModel, Field, model_validator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from tarot_bkd.rider_weite import _SPREAD, _RIDER_WEITE_DECK

CURRENT_DIR = pathlib.Path(__file__).parent


with open(f"{CURRENT_DIR}/spreads.json", "r", encoding="utf-8") as f:
    json_data = json.load(f)

SPREAD_IDS: list[str] = [spread.get("id", "") for spread in json_data.get("spreads", [])]


class SpreadDrawRequest(BaseModel):
    id: str = Field(..., description="Unique identifier for the spread draw request.")
    name: str = Field(..., description="Name of the tarot spread to draw from.")
    arcana: Literal["full", "major", "minor"] = Field("full", description="Arcana type to draw from: 'full', 'major', or 'minor'.")
    orientation: Literal["upright", "reversed", "random"] = Field("random", description="Orientation of drawn cards: 'upright', 'reversed', or 'random'.")
    locale: Literal["en", "zh", "jp"] = Field("en", description="Locale for card and position meanings.")

    @model_validator(mode='before')
    def validate_spread_name(cls, values):
        spread_name = values.get('name')
        if spread_name not in SPREAD_IDS:
            raise ValueError(f"Spread '{spread_name}' not found in registry.")
        return values


def _make_id() -> str:
    return f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}"


_draw_store: dict[str, _SPREAD | None] = {}
_draw_store_lock = threading.Lock()

def build_app() -> FastAPI:
    app = FastAPI()

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    @app.get("/spreads")
    async def list_spreads():
        return {"spreads": SPREAD_IDS}

    @app.post("/draw")
    async def draw_spread(request: SpreadDrawRequest):
        try:
            with _draw_store_lock:
                if request.id in _draw_store:
                    raise ValueError(f"Request ID '{request.id}' already exists.")
                _draw_store[request.id] = None  # Placeholder to reserve the ID

            spread_instance: _SPREAD = _SPREAD(id=request.name, locale=request.locale)
            deck = _RIDER_WEITE_DECK()
            spread_instance.assign_deck(deck)
            spread_instance.draw_assign_cards(arcana=request.arcana, orientation=request.orientation, locale=request.locale)
            drawn_positions = spread_instance.positions

            with _draw_store_lock:
                _draw_store[request.id] = spread_instance  # Store the drawn spread instance

            return {
                "id": request.id,
                "locale": request.locale,
                "spread": {
                    "id": spread_instance.id,
                    "name": spread_instance.i18n.name,
                    "description": spread_instance.i18n.description,
                    "positions": [
                        {
                            "key": pos.key,
                            "name": pos.i18n.name,
                            "description": pos.i18n.description,
                            "card": {
                                "index": pos.card.index,
                                "id": pos.card.id,
                                "name": pos.card.i18n.name,
                                "orientation": pos.card.i18n.orientation,
                                "group": pos.card.i18n.group,
                                "suit": pos.card.i18n.suit,
                                "meanings": pos.card.i18n.meanings,
                            } if pos.card else None
                        }
                        for pos in drawn_positions
                    ]
                }
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
    @app.get("/ids")
    async def list_ids():
        with _draw_store_lock:
            return {"ids": list(_draw_store.keys())}

    @app.post("/cleanup")
    async def cleanup_draws():
        with _draw_store_lock:
            _draw_store.clear()
        return {"status": "success"}

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 开发阶段用 *
        allow_credentials=True,
        allow_methods=["*"],  # 关键：允许 OPTIONS
        allow_headers=["*"],
    )

    return app


if __name__ == "__main__":
    import uvicorn
    app = build_app()
    uvicorn.run(app, host="127.0.0.1", port=8000)

pass
