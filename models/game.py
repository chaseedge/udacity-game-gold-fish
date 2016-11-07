from datetime import date

from google.appengine.ext import ndb

from forms.forms import GameForm, ScoreForm
from models.deck import Deck

import random

class Player(ndb.Model):
    """Creates players for the game"""
    user = ndb.KeyProperty(required=True, kind='User')
    name = ndb.StringProperty(required=True)
    hand = ndb.StringProperty(repeated=True)
    score = ndb.IntegerProperty(required=True, default=0)
    # turn = ndb.BooleanProperty(required=True, default=False)

    def check_pairs(self):
        value_list = [x.split("|")[1].lower() for x in self.hand]
        for card in self.hand:
            print card[1]
            # if card[1] in value_list[i:]:
            #     print card


        print self.hand

class Game(ndb.Model):
    """Game object"""
    player_names = ndb.StringProperty(repeated=True)
    turn = ndb.StringProperty(required=True, default="")
    deck = ndb.StringProperty(repeated=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    winner = ndb.StringProperty()

    @classmethod
    def new_game(cls, user1, user2):
        """Creates and returns a new game"""
        game = cls()
        game_key = game.put()


        player1 = Player(parent=game_key,
                         user=user1.key,
                         name=user1.name)

        player2 = Player(parent=game_key,
                         user=user2.key,
                         name=user2.name)

        # create deck and deal
        deck = Deck()
        deck.create_deck()
        player1.hand = deck.deal_hand()
        player2.hand = deck.deal_hand()
        player1.put()
        player2.put()

        game.player_names.append(player1.name)
        game.player_names.append(player2.name)

        game.deck = deck.deck
        game.turn = player1.name
        game.put()

        return game

    @classmethod
    def make_guess(cls, game, name, guess):
        """Checks players turn and processes players guess"""
        if name.lower() != game.turn.lower():
            return "Sorry, it is not your turn. {} please make a move".format(game.turn)

        else:
            from utils import get_player_by_game
            player_index = game.player_names.index(name)
            if player_index == 0:
                player1 = get_player_by_game(name, game)
                player2 = get_player_by_game(game.player_names[1], game)
            else:
                player1 = get_player_by_game(name, game)
                player2 = get_player_by_game(game.player_names[0], game)

            print player1.name
            print player2.name
            go_fish = True
            guess = guess.lower()

            # loop through player1 hand and make sure card is in hand
            for x in player1.hand:
                value = x.split("|")[1].lower()
                if guess == value:
                    for y in player2.hand:
                        value = y.split("|")[1].lower()
                        if guess == value:
                            player1.score += 1
                            player2.hand.remove(y)
                            player1.hand.remove(x)
                            go_fish = False
                            return "It is a match. Please go again."
            if go_fish:
                card = random.choice(game.deck)
                game.deck.remove(card)
                player1.hand.append(card)
                player1.put()
                game.turn = player2.name
                game.put()
                return "No match, Go fish. You drew {}. Your hand is {}".format(card, player1.hand)




    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.player_names = self.player_names
        form.game_over = self.game_over
        form.turn = self.turn
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

# urlsafe_key = messages.StringField(1, required=True)
#     game_over = messages.BooleanField(2, required=True)
#     players = messages.StringField(3, repeated=True)
#     message = messages.StringField(4, required=True)
#     turn = messages.StringField(5, required=True)

class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    guesses = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                         date=str(self.date), guesses=self.guesses)