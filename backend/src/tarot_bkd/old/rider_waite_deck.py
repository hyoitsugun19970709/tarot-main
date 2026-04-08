import random
from typing import Literal

from tarot_bkd.old.rider_waite_cards import _RIDER_WAITE_CARD


class RIDER_WAITE_DECK(object):
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
            ) -> _RIDER_WAITE_CARD:
        '''
        Get ONE card instance according to identifier (card no. or name), no other operations to deck
          identifier: str of card name of index of card 0 - 77
          orientation: initial drawn orientation
        '''
        if orientation == "random":
            orientation = random.choice(["upright", "reversed"])
        card = _RIDER_WAITE_CARD(identifier=identifier, orientation=orientation, locale=locale)
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
            ) -> list[_RIDER_WAITE_CARD]:
        '''
        Draw number of cards from deck, need to assign deck range and orientation, pop after drawn
          num: number of card to draw
          arcana: arcana to draw from, full or major/minor
          orientation: initial drawn orientation
          pop: pop card after drawn, ensures no replicants
        '''
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


if __name__ == '__main__':
    deck = RIDER_WAITE_DECK()
    cards = deck.draw_cards(num=2, arcana="full", pop=True)
    print(cards)
    for c in cards:
        print(c)
        print(c.i18n)
        pass
    print(deck._deck_drawn)
    cards = deck.draw_cards(num=2, arcana="full", pop=True)
    print(deck._deck_drawn)
    print(deck._deck_full)
    print(deck._deck_major)
    print(deck._deck_minor)
    print("")
    pass

pass
