from datetime import datetime

from google.appengine.ext import ndb

from forms import GameForm
from models.player import Player
from models.move import Move

import json
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
            for r in xrange(2, 15):
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


class Game(ndb.Model):
    """Game object"""
    player_names = ndb.StringProperty(repeated=True)
    turn = ndb.StringProperty(required=False, default="")
    started_on = ndb.DateTimeProperty(required=True, default=datetime.now())
    deck = ndb.JsonProperty()
    history = ndb.JsonProperty(default=[])
    game_over = ndb.BooleanProperty(required=True, default=False)
    matches_to_win = ndb.IntegerProperty(required=True)
    cards_dealt = ndb.IntegerProperty(required=True)
    winner = ndb.StringProperty()
    loser = ndb.StringProperty()

    @classmethod
    def new_game(cls, user1, user2, matches, cards):
        """Creates and returns a new game"""
        game = cls(matches_to_win=matches, cards_dealt=cards)
        game_key = game.put()

        player1 = Player(parent=game_key,
                         user=user1.key,
                         opponent=user2.name,
                         game_url=game.key.urlsafe(),
                         name=user1.name)

        player2 = Player(parent=game_key,
                         user=user2.key,
                         opponent=user1.name,
                         game_url=game.key.urlsafe(),
                         name=user2.name)

        # create deck
        deck = Deck()
        deck.create_deck()

        # deal hand and check for pairs in hand
        player1.hand = deck.deal_hand(cards)
        player1.check_pairs()
        player1.put()

        # deal hand and check for pairs in hand
        player2.hand = deck.deal_hand(cards)
        player2.check_pairs()
        player2.put()

        # check to see if players have ran out of cards or hit target matches
        if player1.check_game_over(matches):
            game.end_game(player1, player2)

        elif player2.check_game_over(matches):
            game.end_game(player2, player1)

        # add player names to the game
        game.player_names.append(player1.name)
        game.player_names.append(player2.name)

        game.deck = deck.deck
        game.turn = player1.name
        game.put()

        return game

    @classmethod
    def make_guess(cls, game, player, guess):
        """Checks players turn and processes players guess"""
        from utils import get_player_by_game

        move = Move(
            parent=game.key,
            player=player.key,
            name=player.name,
            guess=guess,
            match=False,
            game_over=False
        )

        # check to make sure it is the players turns
        if player.name != game.turn:
            move.message = "Sorry, it is not your turn. {} please make a move".format(
                game.turn)
            return move

        else:
            # set player1 and player2
            player_index = game.player_names.index(player.name)
            if player_index == 0:
                opponent = get_player_by_game(game.player_names[1], game)
            else:
                opponent = get_player_by_game(game.player_names[0], game)

            # create a list of card values only
            pl_values = [x['rank'] for x in player.hand]
            opp_values = [x['rank'] for x in opponent.hand]

            # make sure player has their guess in their own hand
            if guess not in pl_values:
                move.message = "Sorry, {} does not have a {} in hand. Please guess again.".format(
                    player.name, guess)
                return move

            else:
                player.history.append(guess)
            # check to see if guess is in player2 hand
            if guess in opp_values:
                move.match = True
                move.message = "Match, please go again."

                # find card in players hand
                pl_index = pl_values.index(guess)
                pl_card = player.hand[pl_index]
                opp_index = opp_values.index(guess)
                opp_card = opponent.hand[opp_index]

                # add match to player1 matches
                player.matches.append(pl_card)
                player.matches.append(opp_card)

                # remove cards from both players hands
                player.hand.remove(pl_card)
                opponent.hand.remove(opp_card)

                player.num_matches += 1

                player.put()
                opponent.put()

                if player.check_game_over(game.matches_to_win):
                    game.end_game(player, opponent)
                    move.game_over = True
                    move.message = "Game over, {} is the winner".format(
                        player.name)
                    return move

                if opponent.check_game_over(game.matches_to_win):
                    game.end_game(opponent, player)
                    move.game_over = True
                    move.message = "Game over, {} is the winner".format(
                        opponent.name)
                    return move

                return move

            else:

                # add the go fish card to players hand and remove from deck
                card = random.choice(game.deck)
                game.deck.remove(card)
                player.hand.append(card)
                player.put()

                # check from matches and if game is over
                player.check_pairs()

                # change game turn
                game.turn = opponent.name
                game.put()

                move.message = "No match, Go fish. {} drew {}".format(
                    player.name, card, player.hand)
                return move

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        from utils import get_player_by_game

        # get players
        player1 = get_player_by_game(self.player_names[0], self)
        player2 = get_player_by_game(self.player_names[1], self)

        form = GameForm()
        form.started_on = self.started_on
        form.urlsafe_key = self.key.urlsafe()
        form.player1 = player1.name
        form.player1_hand = str(player1.hand)
        form.player1_matches = player1.num_matches
        form.player2 = player2.name
        form.player2_hand = str(player2.hand)
        form.player2_matches = player2.num_matches
        form.game_over = self.game_over
        form.matches_to_win = self.matches_to_win

        if not self.game_over:
            form.turn = self.turn
        else:
            form.winner = self.winner

        form.message = message
        return form

    def end_game(self, winner, loser):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        del self.turn
        self.game_over = True
        self.winner = winner.name
        self.loser = loser.name
        self.put()
