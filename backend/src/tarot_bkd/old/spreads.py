import json
import pathlib
from typing import Literal, Any

from tarot_bkd.old.rider_waite_cards import _RIDER_WAITE_CARD
from tarot_bkd.old.rider_waite_deck import RIDER_WAITE_DECK

CURRENT_DIR = pathlib.Path(__file__).parent


class _POSITION(object):
    def __init__(self, spread_id: str, key: str, locale: Literal["en", "zh", "jp"]) -> None:
        self.spread_id: str = spread_id
        self.key: str = key
        self.locale: Literal["en", "zh", "jp"] = locale

        with open(f"{CURRENT_DIR}/spreads.json", "r", encoding="utf-8") as f:
            json_data = json.load(f)
        
        spread_pos_data = next((spread for spread in json_data.get("spreads", []) if spread.get("id", "") == spread_id), {}).get("positions", [])

        self.card: _RIDER_WAITE_CARD | None = None

        self._i18n: dict[str, Any] = next((pos.get("i18n", {}) for pos in spread_pos_data if pos.get("key", "") == key), {})
        self.i18n: dict[str, Any] = self._i18n.get(locale, {})
        pass

    def __repr__(self) -> str:
        if hasattr(self, "card"):
            return f"POSITION({self.key.upper()}, {repr(self.card)})"
        elif hasattr(self, "key"):
            return f"POSITION({self.key}, EMPTY)"
        else:
            return "Empty position"

    def __str__(self) -> str:
        return self.__repr__()

    def draw_card(
            self,
            deck: RIDER_WAITE_DECK,
            arcana: Literal["full", "major", "minor"],
            orientation: Literal["upright", "reversed", "random"],
            pop: bool
        ) -> _RIDER_WAITE_CARD:
        '''
        Draw one card to this position
          deck: card deck instance to draw from
          arcana: deck type to draw from, full or major/minor arcana
          orientation: initial drawn orientation
          pop: pop card after drawn, ensures no replicants
        '''
        self.card = deck.draw_cards(num=1, arcana=arcana, orientation=orientation, pop=pop, locale=self.locale)[0]
        return self.card

    pass


class _SPREAD(object):
    def __init__(self, id: str, locale: Literal["en", "zh", "jp"]) -> None:
        self.id: str = id
        self.locale: Literal["en", "zh", "jp"] = locale
        self._deck_draw: RIDER_WAITE_DECK = RIDER_WAITE_DECK()
        
        with open(f"{CURRENT_DIR}/spreads.json", "r", encoding="utf-8") as f:
            json_data = json.load(f)

        spread_data = next((spread for spread in json_data.get("spreads", []) if spread.get("id", "") == id), None)
        if spread_data is None:
            raise ValueError("Spread not found")
        
        self.positions: list[_POSITION] = [
            _POSITION(spread_id=self.id, key=pos.get("key", ""), locale=self.locale) for pos in spread_data.get("positions", [])
        ]

        self._i18n: dict[str, Any] = spread_data.get("i18n", {})
        self.i18n: dict[str, Any] = self._i18n.get(locale, {})
        pass

    def draw_cards(
            self,
            arcana: Literal["full", "major", "minor"] = "full",
            orientation: Literal["upright", "reversed", "random"] = "random",
            pop: bool = True
        ) -> list[_POSITION]:
        '''Draw cards to all positions in this spread'''
        if self._deck_draw is None:
            raise ValueError("No deck assigned to this spread")
        for pos in self.positions:
            pos.draw_card(deck=self._deck_draw, arcana=arcana, orientation=orientation, pop=pop)
            pass

        return self.positions

    def read_cards(self):
        '''Print position and card info'''
        readings = ""
        for i, pos in enumerate(self.positions):
            if pos.card is None:
                raise ValueError("Empty position")
            readings = readings + f"Position {i+1}\n"
            readings = readings + f"    {pos.i18n.get('name', '')}:".ljust(36)+f"{pos.i18n.get('description', '')}\n"
            readings = readings + f"    {pos.card.i18n.get('name', '')} ({pos.card.i18n.get('orientation', '')}):".ljust(36)+f"{pos.card.i18n.get('meanings', '')}\n"
            pass

        return readings

    pass

if __name__ == '__main__':
    spread = _SPREAD(id="celtic_cross", locale="en")
    print(spread.draw_cards(arcana="full", orientation="random"))
    print(spread.read_cards())
    pass


pass
