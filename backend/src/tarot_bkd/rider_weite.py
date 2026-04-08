import json
import random
import pathlib

from typing import Literal, Any
from dataclasses import dataclass, field

CURRENT_DIR = pathlib.Path(__file__).parent

with open(f"{CURRENT_DIR}/rider_waite_cards.json", "r", encoding="utf-8") as f:
    CARDS_DATA = json.load(f)
with open(f"{CURRENT_DIR}/spreads.json", "r", encoding="utf-8") as f:
    SPREADS_DATA = json.load(f)


@dataclass
class _RIDER_WEITE_CARD_I18N:
    name: str
    group: str
    suit: str | None
    orientation: str
    meanings: str

    def __repr__(self) -> str:
        return f"{self.name} - {self.group} - {self.suit} - {self.orientation}"
    
    def __str__(self) -> str:
        return self.__repr__()

    pass


@dataclass
class _RIDER_WEITE_CARD:
    id: str
    index: int
    number: str
    group: str
    suit: str | None
    orientation: Literal["upright", "reversed"]
    locale: Literal["en", "zh", "jp"]
    i18n: _RIDER_WEITE_CARD_I18N

    def __repr__(self) -> str:
        return f"{self.id}.{self.orientation}"
    
    def __str__(self) -> str:
        if self.group == "major_arcana":
            return f"{self.index} - {self.number} - {self.id} - {self.orientation}"
        elif self.group == "minor_arcana":
            return f"{self.index} - {self.suit} {self.number} - {self.id} - {self.orientation}"
        else:
            return f"{self.id} - {self.orientation}"

    pass


class _RIDER_WEITE_DECK(object):
    def __init__(self) -> None:
        self.reset_deck()
        pass

    def reset_deck(self) -> None:
        '''Reset deck to full'''
        self._deck_full = list(range(78))
        self._deck_major = list(range(22))
        self._deck_minor = list(range(22, 78))
        self._deck_drawn = []
        pass

    @staticmethod
    def get_card(
            identifier: int | str,
            orientation: Literal["upright", "reversed", "random"] = "upright",
            locale: Literal["en", "zh", "jp"] = "en"
        ) -> _RIDER_WEITE_CARD:
        if orientation == "random":
            orientation = random.choice(["upright", "reversed"])
        
        # with open(f"{CURRENT_DIR}/rider_waite_cards.json", "r", encoding="utf-8") as f:
        #     json_data = json.load(f)
        
        cards: list[dict[str, Any]] = CARDS_DATA.get("cards", [])
        positions: dict[str, dict[str, Any]] = CARDS_DATA.get("positions", {})

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
        
        orientation_i18n = pos_data.get(orientation, "")
        card_i18n = _RIDER_WEITE_CARD_I18N(
            name=card_data.get("i18n", {}).get(locale, {}).get("name", ""),
            group=card_data.get("i18n", {}).get(locale, {}).get("group", ""),
            suit=card_data.get("i18n", {}).get(locale, {}).get("suit", None),
            orientation=orientation_i18n,
            meanings=card_data.get("i18n", {}).get(locale, {}).get("meanings", {}).get(orientation, "")
        )
        card = _RIDER_WEITE_CARD(
            id=card_data.get("id", ""),
            index=card_data.get("index", -1),
            number=card_data.get("number", ""),
            group=card_data.get("group", ""),
            suit=card_data.get("suit", None),
            orientation=orientation,
            locale=locale,
            i18n=card_i18n
        )

        return card

    def _get_deck_to_draw(self, arcana: Literal["full", "major", "minor"]) -> list[int]:
        if arcana == "full":
            return self._deck_full
        if arcana == "major":
            return self._deck_major
        if arcana == "minor":
            return self._deck_minor
        raise ValueError("Deck error")
    
    def draw_cards(
            self,
            num: int,
            arcana: Literal["full", "major", "minor"] = "full",
            orientation: Literal["upright", "reversed", "random"] = "random",
            locale: Literal["en", "zh", "jp"] = "en",
            pop: bool = True
        ) -> list[_RIDER_WEITE_CARD]:
        deck_to_draw = self._get_deck_to_draw(arcana)

        if num > len(deck_to_draw):
            raise ValueError(f"Not enough card to draw from deck (draw {num} from {len(deck_to_draw)})")
        
        drawn_indices = random.sample(deck_to_draw, num)
        self._deck_drawn.extend(drawn_indices)
        if pop:
            for di in drawn_indices:
                if di in self._deck_full:
                    self._deck_full.remove(di)
                if di in self._deck_major:
                    self._deck_major.remove(di)
                if di in self._deck_minor:
                    self._deck_minor.remove(di)
                pass

        drawn_cards = [self.get_card(identifier=di, orientation=orientation, locale=locale) for di in drawn_indices]

        return drawn_cards
    
    pass


@dataclass
class _SPREAD_POSITION_I18N:
    name: str
    description: str

    def __repr__(self) -> str:
        return f"{self.name} - {self.description}"
    
    def __str__(self) -> str:
        return self.__repr__()

    pass


@dataclass
class _SPREAD_POSITION:
    key: str
    card: _RIDER_WEITE_CARD | None
    i18n: _SPREAD_POSITION_I18N
    
    def __repr__(self) -> str:
        if self.card is not None:
            return f"{self.key} - {self.card}"
        else:
            return f"{self.key} - EMPTY"
    
    def __str__(self) -> str:
        return self.__repr__()
    
    def assign_card(self, card: _RIDER_WEITE_CARD) -> None:
        self.card = card
        pass

    pass


@dataclass
class _SPREAD_I18N:
    name: str
    description: str

    def __repr__(self) -> str:
        return f"{self.name} - {self.description}"
    
    def __str__(self) -> str:
        return self.__repr__()

    pass


class _SPREAD:
    def __init__(
            self,
            id: str,
            locale: Literal["en", "zh", "jp"] = "en"
        ) -> None:

        spread_data = next((spread for spread in SPREADS_DATA.get("spreads", []) if spread.get("id", "") == id), None)
        if spread_data is None:
            raise ValueError("Spread not found")
        
        pos_data = spread_data.get("positions", [])
        if not pos_data:
            raise ValueError("Spread positions not found")
        
        self.id = id
        self.locale = locale
        self.deck: _RIDER_WEITE_DECK | None = None
        self.i18n = _SPREAD_I18N(
            name=spread_data.get("i18n", {}).get(locale, {}).get("name", ""),
            description=spread_data.get("i18n", {}).get(locale, {}).get("description", "")
        )

        self.positions: list[_SPREAD_POSITION] = []
        for pos in pos_data:
            pos_i18n = _SPREAD_POSITION_I18N(
                name=pos.get("i18n", {}).get(locale, {}).get("name", ""),
                description=pos.get("i18n", {}).get(locale, {}).get("description", "")
            )
            position = _SPREAD_POSITION(
                key=pos.get("key", ""),
                card=None,
                i18n=pos_i18n
            )
            self.positions.append(position)
        
        pass

    def __repr__(self) -> str:
        return f"{self.id} - {len(self.positions)} positions"
    
    def __str__(self) -> str:
        return self.__repr__()
    
    def reset_spread(self) -> None:
        self.deck = None
        for pos in self.positions:
            pos.card = None
        pass
    
    def assign_deck(self, deck: _RIDER_WEITE_DECK) -> None:
        self.deck = deck
        pass

    def draw_assign_cards(
            self,
            arcana: Literal["full", "major", "minor"] = "full",
            orientation: Literal["upright", "reversed", "random"] = "random",
            locale: Literal["en", "zh", "jp"] = "en",
            pop: bool = True
        ) -> None:
        if self.deck is None:
            raise ValueError("Deck not assigned to spread")
        
        drawn_cards = self.deck.draw_cards(
            num=len(self.positions),
            arcana=arcana,
            orientation=orientation,
            locale=locale,
            pop=pop
        )
        for pos, card in zip(self.positions, drawn_cards):
            pos.assign_card(card)
        
        pass

    def print_draw_results(self) -> None:
        print(f"Spread: {self.id}")
        for pos in self.positions:
            print(f"Position: {pos.key}")
            if pos.card is not None:
                print(f"  Card: {pos.card}")
            else:
                print("  Card: EMPTY")
        pass

    def print_draw_results_i18n(self) -> None:
        print(f"Spread: {self.i18n.name} - {self.i18n.description}")
        for pos in self.positions:
            print(f"Position: {pos.i18n.name} - {pos.i18n.description}")
            if pos.card is not None:
                print(f"  Card: {pos.card.i18n.name} - {pos.card.i18n.group} - {pos.card.i18n.suit} - {pos.card.i18n.orientation}")
                print(f"  Meanings: {pos.card.i18n.meanings}")
            else:
                print("  Card: EMPTY")
    
    pass
    


if __name__ == '__main__':
    spread = _SPREAD(id="three_card_spread", locale="en")
    deck = _RIDER_WEITE_DECK()
    spread.assign_deck(deck)
    spread.draw_assign_cards(arcana="full", orientation="random", locale="zh", pop=True)
    # spread.print_draw_results()
    spread.print_draw_results_i18n()
    pass


pass
