# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""

import endpoints
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from protorpc import remote, messages, message_types

from forms import StringMessage, GameForm, AllGames, AllUsersForm, AllUserGames, ScoreBoard, CancelGame
from models.game import Game
from models.player import Player
from models.user import User
from utils import get_by_urlsafe, check_user_exists, get_player_by_game, check_game_exists

NEW_GAME_REQUEST = endpoints.ResourceContainer(
    player1 = messages.StringField(1, required=True),
    player2 = messages.StringField(2, required=True),
    cards_dealt = messages.IntegerField(3, required=False),
    matches_to_win = messages.IntegerField(4, required=False))

USER_GAMES_REQUEST = endpoints.ResourceContainer(
    username = messages.StringField(1, required=True))

GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1))

CANCEL_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),
    cancel=messages.BooleanField(2))

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

MEMCACHE_SCOREBOARD = 'SCOREBOARD'

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
        user_name = request.user_name.title()
        if User.query(User.name == user_name).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!')
        user = User(name=user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                            request.user_name))

    @endpoints.method(response_message=AllUsersForm,
                      path='user/all',
                      name='get_all_users',
                      http_method='GET')
    def get_all_users(self, request):
        """Returns list of all users"""
        return AllUsersForm(users=[user.name for user in User.query()])

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

        # set to low number for testing purposes. makes game go faster
        matches = request.matches_to_win
        if not matches:
            matches = 6

        # number of cards in hand to be dealt
        cards = request.cards_dealt
        if not cards:
            cards = 5

        # make sure players don't have an active game already
        game = check_game_exists(player1.name, player2.name)
        if game:
            return game.to_form('Game already exists')

        try:
            game = Game.new_game(player1, player2, matches, cards)
        except ValueError:
            raise endpoints.BadRequestException('Two valid users are needed')


        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        taskqueue.add(url='/tasks/cache_scoreboard')

        if game.game_over:
            return game.to_form("Game over, {} is the winner".format(game.winner))
        return game.to_form('Please make guess')

    @endpoints.method(request_message=USER_GAMES_REQUEST,
                      response_message=AllUserGames,
                      path='user/{username}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Returns all games for a given user"""
        user = check_user_exists(request.username)
        players = Player.query(Player.user == user.key)
        # print "Game key is {}".format(players.key.parent())
        if players.count() >= 1:
            return AllUserGames(games=[player.to_form() for player in players])
        else:
            raise endpoints.NotFoundException('No games found for user {}'.format(user.name))

    @endpoints.method(request_message=CANCEL_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/cancel',
                      name='cancel_game',
                      http_method='POST')
    def cancel_game(self, request):
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        # make sure user selected true
        if not request.cancel:
            return StringMessage(message="Must select true to be deleted")

        # check to see if game is already over
        if game.game_over:
            return StringMessage(message="Sorry, Game cannot be deleted. Game is already over.")

        if game and request.cancel:

            # delete players associated with game
            players = Player.query(ancestor=game.key)
            for player in players:
                player.key.delete()

            # delete game key
            game.key.delete()

            return StringMessage(message="Game and players deleted")


    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        if game.game_over:
            return game.to_form("Game over, {} is the winner".format(game.winner))

        if game:
            return game.to_form('Your move {}'.format(game.turn))

        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(response_message=AllGames,
                      path='games',
                      name='get_all_games',
                      http_method='GET')
    def get_all_games(self, request):
        """Returns all games"""
        games = Game.query()

        if games.count() >= 1:
            return AllGames(games=[game.to_form("n/a") for game in games])
        else:
            raise endpoints.NotFoundException('No games found')


    @endpoints.method(request_message=HAND_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/{player_name}/hand',
                      name='get_player_hand',
                      http_method='GET')
    def get_player_hand(self, request):
        """Get players hand"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        if game.game_over:
            return StringMessage(message='Game over, {} is the winner'.format(game.winner))

        player = get_player_by_game(request.player_name, game)

        if player:
            return StringMessage(message='{} has {}'.format(player.name,
                player.hand))
        else:
            raise endpoints.NotFoundException('Player not found!')


    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='GET')
    def make_move(self, request):
        """Player Makes Guess. Returns results"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            raise endpoints.NotFoundException('Game already over')

        player = get_player_by_game(request.player_name, game)
        if not player:
            raise endpoints.NotFoundException('Player is not in this game')

        guess = request.guess.title()

        # see check if user entered Jacks instead of Jack
        if guess[-1] == "s":
            guess = guess[:-1]

        message = game.make_guess(game,player.name,guess)

        # update cache_scoreboard
        taskqueue.add(url='/tasks/cache_scoreboard')

        return StringMessage(message=message)


    @endpoints.method(response_message=ScoreBoard,
                      path='games/scoreboard',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Get the cached ScoreBoard"""
        users = User.query().order(User.losses)
        return ScoreBoard(scores=[memcache.get(str(user.name)) for user in users])


    @staticmethod
    def _cache_scoreboard():
        """Populates memcache with the average moves remaining of Games"""
        users = User.query()
        games = Game.query()
        players = Player.query()

        for user in users:
            user.wins = games.filter(Game.winner == user.name).count()
            user.losses = games.filter(Game.loser == user.name).count()
            score = "{} {}-{}".format(user.name, user.wins, user.losses)
            memcache.set(str(user.name), str(score))
            user.put()

api = endpoints.api_server([GoFishApi])
