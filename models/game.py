from datetime import date

from google.appengine.ext import ndb

from forms.forms import GameForm, ScoreForm
from models.deck import Deck
from utils import get_by_urlsafe
import random

class Player(ndb.Model):
    """Creates players for the game"""
    game = ndb.KeyProperty(required=True, kind='Game')
    user = ndb.KeyProperty(required=True, kind='User')
    hand = ndb.StringProperty(repeated=True)
    score = ndb.IntegerProperty(required=True, default=0)
    turn = ndb.BooleanProperty(required=True, default=False)

    @classmethod
    def new_player(cls, game_key, user_key):
        player = cls(game=game_key,
                     user=user_key)


class Game(ndb.Model):
    """Game object"""
    player1 = ndb.KeyProperty(required=True, kind='User')
    player1_hand = ndb.StringProperty(repeated=True)
    player1_score = ndb.IntegerProperty(required=True, default=0)
    player1_turn = ndb.BooleanProperty(required=True, default=True)
    player2 = ndb.KeyProperty(required=True, kind='User')
    player2_hand = ndb.StringProperty(repeated=True)
    player2_score = ndb.IntegerProperty(required=True, default=0)
    deck = ndb.StringProperty(repeated=True)
    game_over = ndb.BooleanProperty(required=True, default=False)

    @classmethod
    def new_game(cls, player1_key, player2_key):
        """Creates and returns a new game"""
        game = cls(player1=player1_key,
                    player2=player2_key)

        # create deck and deal
        deck = Deck()
        deck.create_deck()
        game.player1_hand = deck.deal_hand()
        game.player2_hand = deck.deal_hand()
        game.deck = deck.deck
        game.put()

        return game

    @classmethod
    def make_guess(cls, game, player, guess):
        """Checks players turn and processes players guess"""

        # check if it's players turn
        if player.key == game.player1 and game.player1_turn:
            game.player1_turn = False
            go_fish = True

            # loop through player1 hand and make sure card is in hand
            for x in game.player1_hand:
                if guess.lower() == (x.split("|")[1]).lower():
                    for y in game.player2_hand:
                        if guess.lower() == (y.split("|")[1]).lower():
                            message = "It is a match. Please go again."
                            game.player1_score += 1
                            game.player2_hand.remove(y)
                            game.player1_hand.remove(x)
                            game.player1_turn = True
                            go_fish = False
                            return message
            if go_fish:
                card = random.choice(game.deck)
                game.deck.remove(card)
                game.player1_hand.append(card)
                message = "No match, Go fish. You drew {}".format(card)
                game.put()
                print game.player1_hand
                return message

        return "It's not your turn"



    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.player1 = self.player1.get().name
        form.player2 = self.player2.get().name
        form.game_over = self.game_over
        form.player1_hand = self.player1_hand
        form.player2_hand = self.player2_hand
        form.player1_turn = True
        form.message = message
        return form

    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(), won=won,
                      guesses=self.attempts_allowed - self.attempts_remaining)
        score.put()



class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    guesses = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                         date=str(self.date), guesses=self.guesses)