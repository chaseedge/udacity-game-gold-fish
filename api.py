# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""

import endpoints
from google.appengine.ext import ndb
from google.appengine.api import (taskqueue)
from protorpc import (
    remote,
    messages,
    message_types)

from forms import (
    StringMessage,
    StringRepeatedMessage,
    GameForm,
    AllGamesForm,
    AllUserGamesForm,
    GameHistoryForm,
    AllGameHistory,
    PlayerHandForm,
    AllUserScores,
    MoveForm)
from models.game import (
    Game,
    faces)
from models.player import Player
from models.move import Move
from models.user import User
from utils import (
    get_by_urlsafe,
    check_user_exists,
    get_player_by_game)

NEW_GAME_REQUEST = endpoints.ResourceContainer(
    player1=messages.StringField(1, required=True),
    player2=messages.StringField(2, required=True),
    cards_dealt=messages.IntegerField(3, required=False),
    matches_to_win=messages.IntegerField(4, required=False))

USER_GAMES_REQUEST = endpoints.ResourceContainer(
    username=messages.StringField(1, required=True),
    active_only=messages.BooleanField(2, required=True))

GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1))

GET_ALL_GAMES_REQUEST = endpoints.ResourceContainer(
    active_only=messages.BooleanField(1, required=False))

CANCEL_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1))

HAND_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1, required=True),
    username=messages.StringField(2, required=True))

USER_REQUEST = endpoints.ResourceContainer(
    username=messages.StringField(1, required=True),
    email=messages.StringField(2))

MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1, required=True),
    username=messages.StringField(2, required=True),
    guess=messages.StringField(3, required=True))

GAME_HISTORY_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1, required=True))


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
        username = request.username.title()

        # check to see if user already exists
        if User.query(User.name == username).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!')
        else:
            user = User(name=username, email=request.email)
            user.put()

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        taskqueue.add(url='/tasks/cache_scoreboard')

        return StringMessage(message='User {} created!'.format(
            request.username))

    @endpoints.method(response_message=StringRepeatedMessage,
                      path='user/all',
                      name='get_all_users',
                      http_method='GET')
    def get_all_users(self, request):
        """Returns list of all users"""
        users = User.query()

        # make sure there are users
        if users.count() == 0:
            raise endpoints.NotFoundException('No users found')

        return StringRepeatedMessage(messages=[user.name for user in users])

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""

        # make sure players exists, returns player or raises error
        player1 = check_user_exists(request.player1)
        player2 = check_user_exists(request.player2)

        # check to see if two unique players
        if player1.name == player2.name:
            raise endpoints.ConflictException('Two unique users needed')

        # set defaults
        matches = request.matches_to_win
        if not matches:
            matches = 6

        # defaut number of cards in hand to be dealt
        cards = request.cards_dealt
        if not cards:
            cards = 5

        # make sure players don't have an active game already
        game = Game.query(ndb.AND(Game.player_names == player1.name,
                                  Game.player_names == player2.name,
                                  Game.game_over == False)).get()

        if game:
            return game.to_form('Game already exists')
        else:
            game = Game.new_game(player1, player2, matches, cards)

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        taskqueue.add(url='/tasks/cache_scoreboard')

        if game.game_over:
            return game.to_form(
                "Game over, {} is the winner".format(
                    game.winner))

        return game.to_form('Please make guess')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        if game.game_over:
            return game.to_form(
                "Game over, {} is the winner".format(
                    game.winner))

        if game:
            return game.to_form('Your move {}'.format(game.turn))

        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=USER_GAMES_REQUEST,
                      response_message=AllGamesForm,
                      path='user/{username}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Returns all games for a given user"""

        # check to see if username is valid
        user = check_user_exists(request.username)

        games = Game.query(ndb.AND(Game.player_names == user.name))
        error_msg = 'No games found for user {}'.format(user.name)

        # get active_only games by filtering game_over = false
        if request.active_only:
            games = games.filter(Game.game_over != request.active_only)
            error_msg = 'No active games found for user {}'.format(user.name)

        if games.count():
            return AllGamesForm(games=[game.to_form("n/a") for game in games])
        else:
            raise endpoints.NotFoundException(error_msg)

    @endpoints.method(request_message=GET_ALL_GAMES_REQUEST,
                      response_message=AllGamesForm,
                      path='games',
                      name='get_all_games',
                      http_method='GET')
    def get_all_games(self, request):
        """Returns all games"""

        if request.active_only:
            games = Game.query(Game.game_over == False)
        else:
            games = Game.query()

        if games.count() >= 1:
            return AllGamesForm(games=[game.to_form("n/a") for game in games])
        else:
            raise endpoints.NotFoundException('No games found')

    @endpoints.method(request_message=CANCEL_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/cancel',
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        """Cancel a game that is in progress."""
        """
        Args:
            request: The CANCEL_GAME_REQUEST object.
        Returns:
            A message that is sent to the client, saying that the
            game has been cancelled.
        Raises:
            endpoints.NotFoundException: If the game isn't found.
            endpoints.ForbiddenException: If the game is completed already it
            cannot be cancelled."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        if not game:
            raise endpoints.NotFoundException('Game not found.')
        if game.game_over:
            raise endpoints.ForbiddenException(
                'Cannot cancel a completed game.')

        players = Player.query(ancestor=game.key)
        for player in players:
            player.key.delete()

        game.key.delete()
        return StringMessage(message='Your game was succesfully cancelled.')

    @endpoints.method(request_message=HAND_REQUEST,
                      response_message=PlayerHandForm,
                      path='game/{urlsafe_game_key}/player/{username}/hand',
                      name='get_player_hand',
                      http_method='GET')
    def get_player_hand(self, request):
        """Get players hand"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        if game.game_over:
            raise endpoints.ForbiddenException(
                'Illegal action: Game is already over.')

        player = get_player_by_game(request.username, game)

        if player:
            return PlayerHandForm(hand=str(player.hand),
                                  matches=str(player.matches))
        else:
            raise endpoints.NotFoundException('Player not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=MoveForm,
                      path='game/{urlsafe_game_key}/player/{username}/move',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Player Makes Guess. Returns results"""
        guess = request.guess.title()

        # check and return if valid game
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        if game.game_over:
            raise endpoints.ForbiddenException(
                'Illegal action: Game is already over.')

        # check to see if user is valid and is in the game
        player = get_player_by_game(request.username, game)

        if not player:
            raise endpoints.NotFoundException('Player is not in this game')

        # make sure guess is valid. Check numbers and then faces
        try:

            if int(guess) > 1 and int(guess) < 11:
                move = game.make_guess(game, player, guess)

            else:
                raise endpoints.BadRequestException('Invalid Guess')

        except:

            # build list of face cards to check guess against
            face_cards = []
            for key, value in faces.iteritems():
                face_cards.append(value)

            # see check if user entered Jacks instead of Jack
            if guess[-1] == "s":
                guess = guess[:-1]

            # Since guess is not a number, check if a valid face card
            if guess in face_cards:
                move = game.make_guess(game, player, guess)
            else:
                raise endpoints.BadRequestException('Invalid Guess')

        # refresh player entity for any changes to hand
        player = get_player_by_game(request.username, game)

        move.put()

        # update cache_scoreboard
        taskqueue.add(url='/tasks/cache_scoreboard')

        return MoveForm(message=move.message,
                        match=move.match,
                        hand=str(player.hand),
                        num_matches=player.num_matches,
                        game_over=move.game_over)

    @endpoints.method(request_message=GAME_HISTORY_REQUEST,
                      response_message=AllGameHistory,
                      path='game/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Get user's guess history"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        moves = Move.query(ancestor=game.key).order(Move.time)

        if moves.count():
            return AllGameHistory(history=[move.to_form() for move in moves])

        else:
            raise endpoints.NotFoundException(
                'Game does not have any moves logged')

    @endpoints.method(response_message=AllUserScores,
                      path='games/scoreboard',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Get the ScoreBoard"""
        users = User.query().order(-User.win_ratio, -User.games)

        if not users.count():
            raise endpoints.NotFoundException('No users found')

        else:
            return AllUserScores(scores=[user.to_form() for user in users])

    @staticmethod
    def _cache_scoreboard():
        """Populates User win/loss records for the scoreboard"""
        games = Game.query()
        users = User.query()

        for user in users:
            user.wins = games.filter(Game.winner == user.name).count()
            user.losses = games.filter(Game.loser == user.name).count()
            user.games = user.wins + user.losses

            if user.games:
                user.win_ratio = float(user.wins) / float(user.games)

            user.put()

api = endpoints.api_server([GoFishApi])
