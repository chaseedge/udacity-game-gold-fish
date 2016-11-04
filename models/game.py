from datetime import date

from google.appengine.ext import ndb

from forms.forms import GameForm, ScoreForm
from models.deck import Deck


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
        game = Game(player1=player1_key,
                    player2=player2_key,
                    game_over=False)

        # create deck and deal
        deck = Deck()
        deck.create_deck()
        game.player1_hand = deck.deal_hand()
        game.player2_hand = deck.deal_hand()
        game.deck = deck.deck
        game.put()

        return game

    @classmethod
    def make_guess(cls, player_name, guess):
        pass
        # player = check_player_exists(player_name)
        # if player.key == cls.player1 and cls.player1_turn == True:
        #     for x in cls.player2_hand:
        #         if guess == x.split("|")[1]:
        #             print "Yes %s" % guess



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