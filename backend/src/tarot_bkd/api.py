from __future__ import annotations

import json
import sys
import pathlib
import threading
import os
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

import anthropic

from tarot_bkd.rider_weite import _SPREAD, _RIDER_WEITE_DECK

CURRENT_DIR = pathlib.Path(__file__).parent


# MiniMax AI client
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
ANTHROPIC_BASE_URL = "https://api.minimaxi.com/anthropic"


def _get_ai_client():
    return anthropic.Anthropic(
        base_url=ANTHROPIC_BASE_URL,
        api_key=MINIMAX_API_KEY,
    )


TAROT_SYSTEM_PROMPT = """You are an experienced Tarot reader with deep knowledge of both Rider-Waite cards and psychological insight. You speak in a warm, empathetic but grounded tone. When interpreting spreads:
- Explain each card's meaning in the context of its POSITION (position matters enormously in Tarot)
- Show how the cards interact with each other
- Give practical, actionable guidance rather than vague predictions
- Be honest about tensions or warnings in the cards without being alarmist
- Always connect the interpretation back to the querent's specific question

Respond in the same language the user used to ask their question."""


def _build_interpretation_prompt(question: str, spread_data: dict) -> str:
    spread_name = spread_data.get("name", "Unknown")
    positions = spread_data.get("positions", [])

    cards_text = []
    for i, pos in enumerate(positions, 1):
        card = pos.get("card") or {}
        card_name = card.get("name", "Unknown")
        orientation = card.get("orientation", "unknown")
        meanings = card.get("meanings", "")
        pos_name = pos.get("name", "")
        pos_desc = pos.get("description", "")
        emoji = "🔃" if orientation == "reversed" else "⬆️"
        cards_text.append(
            f"Position {i}: {pos_name} ({pos_desc})\n"
            f"  Card: {card_name} {emoji}\n"
            f"  Meaning: {meanings}"
        )

    return f"""Querent's question: {question}

Spread: {spread_name}

Drawn cards:
{"\n\n".join(cards_text)}

Please provide a thoughtful, empathetic Tarot interpretation addressing the querent's question. Structure your response to cover each card in position, then synthesize how they work together to answer the question."""


RECOMMEND_SYSTEM_PROMPT = """You are a Tarot expert. Based on the user's question, recommend the most suitable tarot spread.

Available spreads:
- three_card_spread: For simple, direct questions. Gives quick insight on past-present-future or situation-advice-outcome.
- celtic_cross: For complex situations, relationships, major life decisions. Provides comprehensive 10-position analysis.

Rules:
- Simple questions (yes/no, should I do X) → three_card_spread
- Complex questions (relationships, career crossroads, deep emotional issues) → celtic_cross
- Reply in JSON format: {"spread": "spread_id", "reason": "brief explanation in Chinese"}
- Only output JSON, no other text."""


def _build_recommend_prompt(question: str) -> str:
    return f"""User's question: {question}

Recommend the most suitable spread. Reply only in JSON format with fields "spread" (spread id) and "reason" (brief Chinese explanation)."""


class InterpretRequest(BaseModel):
    question: str = Field(..., description="The querent's question to the Tarot.")
    spread: dict = Field(..., description="The spread data including positions and cards.")


class RecommendRequest(BaseModel):
    question: str = Field(..., description="The querent's question to the Tarot.")


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

    @app.post("/recommend-spread")
    async def recommend_spread(request: RecommendRequest):
        question = request.question.lower()

        # Rule-based fallback - used when AI is unavailable
        def rule_based_recommend(q: str):
            complex_keywords = ["爱情", "感情", "关系", "复合", "分手", "离婚", "婚姻", "恋人", "暧昧", "出轨",
                                "工作", "辞职", "跳槽", "事业", "职业", "创业", "投资", "金钱", "财运",
                                "健康", "疾病", "手术", "学业", "考试", "升学", "出国", "移民",
                                "人生", "命运", "方向", "选择", "困惑", "迷茫", "焦虑"]
            for kw in complex_keywords:
                if kw in q:
                    return ("celtic_cross", f"你的问题涉及「{kw}」等复杂因素，建议使用凯尔特十字（10张牌）进行全面分析")
            return ("three_card_spread", "这是一个简单直接的问题，适合用三张牌阵快速解读")

        try:
            prompt = _build_recommend_prompt(request.question)

            client = _get_ai_client()
            response = client.messages.create(
                model="MiniMax-M2.7-highspeed",
                max_tokens=500,
                thinking={"type": "disabled"},
                system=RECOMMEND_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )

            recommendation = ""
            for block in response.content:
                if hasattr(block, "text") and block.text:
                    recommendation = block.text.strip()
                    break

            if not recommendation:
                spread_id, reason = rule_based_recommend(request.question)
                return {"spread": spread_id, "reason": reason, "fallback": True}

            # Parse JSON response - strip markdown code blocks if present
            import json, re
            try:
                # Remove markdown code block markers
                cleaned = re.sub(r'^```json\s*', '', recommendation)
                cleaned = re.sub(r'^```\s*', '', cleaned)
                cleaned = re.sub(r'\s*```$', '', cleaned)
                rec_data = json.loads(cleaned)
                spread_id = rec_data.get("spread", "three_card_spread")
                reason = rec_data.get("reason", "")
            except:
                # Fallback if JSON parse fails
                spread_id, reason = rule_based_recommend(request.question)
                return {"spread": spread_id, "reason": reason, "fallback": True}

            return {"spread": spread_id, "reason": reason}

        except anthropic.APIStatusError as e:
            if e.status_code == 529:
                # AI overloaded - use rule-based fallback
                spread_id, reason = rule_based_recommend(request.question)
                return {"spread": spread_id, "reason": reason, "fallback": True}
            raise HTTPException(status_code=e.status_code, detail=f"AI API error: {e.message}")
        except Exception as e:
            spread_id, reason = rule_based_recommend(request.question)
            return {"spread": spread_id, "reason": reason, "fallback": True}

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

    @app.post("/interpret")
    async def interpret_spread(request: InterpretRequest):
        try:
            prompt = _build_interpretation_prompt(request.question, request.spread)

            client = _get_ai_client()
            response = client.messages.create(
                model="MiniMax-M2.7-highspeed",
                max_tokens=1500,
                thinking={"type": "disabled"},
                system=TAROT_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract text from response blocks
            interpretation = ""
            for block in response.content:
                if hasattr(block, "text"):
                    interpretation = block.text
                    break

            if not interpretation:
                raise HTTPException(status_code=500, detail="AI returned no text")

            return {"interpretation": interpretation}

        except anthropic.APIStatusError as e:
            raise HTTPException(status_code=e.status_code, detail=f"AI API error: {e.message}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

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
