# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""

import endpoints
import random
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from protorpc import remote, messages

from forms.forms import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    ScoreForms
from models.game import Game, Score, Player
from models.user import User
from utils import get_by_urlsafe, check_user_exists, get_player_by_game, check_game_exists

NEW_GAME_REQUEST = endpoints.ResourceContainer(
    NewGameForm)

GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)

HAND_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1, required=True),
    player_name=messages.StringField(2, required=True))

USER_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1, required=True),
    email=messages.StringField(2))

MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1, required=True),
    player_name=messages.StringField(2, required=True),
    guess=messages.StringField(3, required=True))

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

@endpoints.api(name='go_fish', version='v1')
class GoFishApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name.title(), email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""

        # make sure players exists
        player1 = check_user_exists(request.player1)
        player2 = check_user_exists(request.player2)

        # make sure players don't have an active game already
        game = check_game_exists(player1.name, player2.name)
        if game:
            return game.to_form('Game already exists')

        try:
            game = Game.new_game(player1, player2)
        except ValueError:
            raise endpoints.BadRequestException('Two valid users are needed')


        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        # taskqueue.add(url='/tasks/cache_average_attempts')
        return game.to_form('Please make guess')


    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        if game:
            return game.to_form('Your move {}'.format(game.turn))
        else:
            raise endpoints.NotFoundException('Game not found!')


    @endpoints.method(request_message=HAND_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/{player_name}/hand',
                      name='get_player_hand',
                      http_method='GET')
    def get_player_hand(self, request):
        """Get players hand"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        player = get_player_by_game(request.player_name, game)
        player.check_pairs()

        if player:
            return StringMessage(message='{} has {}'.format(player.name,
                player.hand))
        else:
            raise endpoints.NotFoundException('Player not found!')


    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Player Makes Guess. Returns results"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            raise endpoints.NotFoundException('Game already over')

        player = get_player_by_game(request.player_name, game)
        if not player:
            raise endpoints.NotFoundException('Player is not in this game')

        guess = request.guess.lower()

        # see check if user entered Jacks instead of Jack
        if guess[-1] == "s":
            guess = guess[:-1]

        message = game.make_guess(game,player.name,guess)

        return StringMessage(message=message)

        # if game.game_over:
        #     return game.to_form('Game already over!')
        # else:
        #     return game.to_form('Good work')

        # game.attempts_remaining -= 1
        # if request.guess == game.target:
        #     game.end_game(True)
        #     return game.to_form('You win!')
        #
        # if request.guess < game.target:
        #     msg = 'Too low!'
        # else:
        #     msg = 'Too high!'
        #
        # if game.attempts_remaining < 1:
        #     game.end_game(False)
        #     return game.to_form(msg + ' Game over!')
        # else:
        #     game.put()
        #     return game.to_form(msg)

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(response_message=StringMessage,
                      path='games/average_attempts',
                      name='get_average_attempts_remaining',
                      http_method='GET')
    def get_average_attempts(self, request):
        """Get the cached average moves remaining"""
        return StringMessage(message=memcache.get(MEMCACHE_MOVES_REMAINING) or '')

    @staticmethod
    def _cache_average_attempts():
        """Populates memcache with the average moves remaining of Games"""
        games = Game.query(Game.game_over == False).fetch()
        # if games:
        #     count = len(games)
        #     total_attempts_remaining = sum([game.attempts_remaining
        #                                 for game in games])
        #     average = float(total_attempts_remaining)/count
        #     memcache.set(MEMCACHE_MOVES_REMAINING,
        #                  'The average moves remaining is {:.2f}'.format(average))


api = endpoints.api_server([GoFishApi])
