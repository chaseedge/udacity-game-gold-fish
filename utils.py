"""utils.py - File for collecting general utility functions."""

import logging
from google.appengine.ext import ndb
from models.game import Game
from models.player import Player
from models.user import User

import endpoints

def get_by_urlsafe(urlsafe, model):
    """Returns an ndb.Model entity that the urlsafe key points to. Checks
        that the type of entity returned is of the correct kind. Raises an
        error if the key String is malformed or the entity is of the incorrect
        kind
    Args:
        urlsafe: A urlsafe key string
        model: The expected entity kind
    Returns:
        The entity that the urlsafe Key string points to or None if no entity
        exists.
    Raises:
        ValueError:"""
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    except Exception, e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()
    if not entity:
        return None
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')
    return entity


def check_user_exists(name):
    """Checks to see if User exits and returns user"""
    user = User.query(User.name == name.title()).get()
    if not user:
        raise endpoints.NotFoundException(
            'User {} does not exist!'.format(name))
    else:
        return user


def get_player_by_game(name, game):
    """Search for player given name and game"""

    # check to make sure User exists
    if not check_user_exists(name):
        raise endpoints.NotFoundException(
            '{} does not exist!'.format(name))

    #check to see if Player is in this game
    player = Player.query(ancestor=game.key).filter(Player.name == name.title()).get()
    if not player:
        raise endpoints.NotFoundException(
            '{} does not exist!'.format(name))
    else:
        return player


def check_game_exists(player1, player2):
    """Checks to see if the two players already have a game"""
    game = Game.query(ndb.AND(Game.player_names == player1,
                              Game.player_names == player2,
                              Game.game_over == False)).get()
    return game
