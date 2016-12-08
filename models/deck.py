import random

suits = {
    0: "Spades",
    1: "Clubs",
    2: "Hearts",
    3: "Diamonds"
}
faces = {
    11: "Jack",
    12: "Queen",
    13: "King",
    14: "Ace"
}

class Deck(object):
    def __init__(self):
        self.deck = []

    def create_deck(self):
        for s in xrange(4):
            for r in xrange(2,15):
                if r > 10:
                    r = faces[r]
                card = {
                    'suit': suits[s],
                    'rank': str(r)
                }
                self.deck.append(card)

    def deal_hand(self, cards_to_deal):
        hand = []
        for i in xrange(cards_to_deal):
            card = random.choice(self.deck)
            self.deck.remove(card)
            hand.append(card)
        return hand



