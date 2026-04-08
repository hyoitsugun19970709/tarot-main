import json
import pathlib

from typing import Literal, Any
from dataclasses import dataclass, field

CURRENT_DIR = pathlib.Path(__file__).parent


@dataclass
class _RIDER_WAITE_CARD:
    def __init__(
            self,
            identifier: int | str,
            orientation: Literal["upright", "reversed"] = "upright",
            locale: Literal["en", "zh", "jp"] = "en"
        ) -> None:
        if orientation not in ["upright", "reversed"]:
            raise ValueError("Orientation error")

        with open(f"{CURRENT_DIR}/rider_waite_cards.json", "r", encoding="utf-8") as f:
            json_data = json.load(f)
        cards: list[dict[str, Any]] = json_data.get("cards", [])
        positions: dict[str, dict[str, Any]] = json_data.get("positions", {})

        if type(identifier) == int:
            card_data = next((card for card in cards if card.get("index", -1) == identifier), None)
        elif type(identifier) == str:
            card_data = next((card for card in cards if card.get("id", "").lower() == identifier.lower()), None)
        else:
            raise ValueError("Identifier error")
        
        pos_data = positions.get("i18n", {}).get(locale, "")

        if card_data is None:
            raise ValueError("Card not found")
        if pos_data is None:
            raise ValueError("Card position i18n not found")

        self.locale = locale
        self.id = card_data.get("id", "")
        self.index = card_data.get("index", -1)
        self.number = card_data.get("number", "")
        self.group = card_data.get("group", "")
        self.suit = card_data.get("suit", "")
        self.orientation = orientation

        self._i18n = card_data.get("i18n", {})
        self.i18n = self._i18n.get(locale, {})
        self.i18n["orientation"] = pos_data.get(orientation, "")
        self.i18n["meanings"] = self._i18n.get(self.locale, "").get("meanings", {}).get(orientation, "")
        pass

    def __repr__(self) -> str:
        return f"{self.id}.{self.orientation}"

    def __str__(self) -> str:
        if self.group == "major_arcana":
            return f"{self.index} - {self.number} - {self.id} - {self.orientation}"
        elif self.group == "minor_arcana":
            return f"{self.index} - {self.suit} {self.number} - {self.id} - {self.orientation}"
        raise ValueError("Card error")

    def toggle_orientation(self) -> None:
        if self.orientation == "upright":
            self.orientation = "reversed"
        elif self.orientation == "reversed":
            self.orientation = "upright"
        else:
            raise ValueError("Orientation error")

    def to_orientation(self, to_state: Literal["upright", "reversed"]) -> None:
        self.orientation = to_state
        pass

    pass


pass
