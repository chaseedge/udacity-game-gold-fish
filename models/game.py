from datetime import datetime

from google.appengine.ext import ndb

from forms import GameForm
from models.deck import Deck
from models.player import Player

import json
import random


class Game(ndb.Model):
    """Game object"""
    player_names = ndb.StringProperty(repeated=True)
    turn = ndb.StringProperty(required=False, default="")
    started_on = ndb.DateTimeProperty(required=True, default=datetime.now())
    deck = ndb.JsonProperty()
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
    def make_guess(cls, game, name, guess):
        """Checks players turn and processes players guess"""
        from utils import get_player_by_game

        # check to make sure it is the players turns
        if name.title() != game.turn:
            return "Sorry, it is not your turn. {} please make a move".format(
                game.turn)

        else:
            # set player1 and player2
            player_index = game.player_names.index(name)
            if player_index == 0:
                player1 = get_player_by_game(name, game)
                player2 = get_player_by_game(game.player_names[1], game)
            else:
                player1 = get_player_by_game(name, game)
                player2 = get_player_by_game(game.player_names[0], game)

            # create a list of values only
            pl1_values = [x['rank'] for x in player1.hand]
            pl2_values = [x['rank'] for x in player2.hand]

            # make sure player has their guess in their own hand
            if guess not in pl1_values:
                return "Sorry, you do not have a {} in your own hand. Please guess again.".format(
                    guess)
            else:
                print "trying to add card to player history {}".format(guess)
                player1.history.append(guess)
            # check to see if guess is in player2 hand
            if guess in pl2_values:

                # find card in players hand
                pl1_index = pl1_values.index(guess)
                pl1_card = player1.hand[pl1_index]

                pl2_index = pl2_values.index(guess)
                pl2_card = player2.hand[pl2_index]

                # add match to player1 matches
                player1.matches.append(pl1_card)
                player1.matches.append(pl2_card)

                # remove cards from both players hands
                player1.hand.remove(pl1_card)
                player2.hand.remove(pl2_card)

                player1.num_matches += 1

                player1.put()
                player2.put()

                if player1.check_game_over(game.matches_to_win):
                    game.end_game(player1, player2)
                    return "Game over, {} is the winner".format(player1.name)

                if player2.check_game_over(game.matches_to_win):
                    game.end_game(player2, player1)
                    return "Game over, {} is the winner".format(player2.name)

                return "Match, please go again."

            else:

                # add the go fish card to players hand and remove from deck
                card = random.choice(game.deck)
                game.deck.remove(card)
                player1.hand.append(card)
                player1.put()

                # check from matches and if game is over
                player1.check_pairs()

                # change game turn
                game.turn = player2.name
                game.put()
                return "No match, Go fish. You drew {}. Your hand is {}".format(
                    card, player1.hand)

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
