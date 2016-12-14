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
    except Exception as e:
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


def check_user_exists(username):
    """Returns an User (ndb.Model) entity that the username points to. Raises an
        error if an entity is not found.
    Args:
        username: Username string
    Returns:
        The entity that the username string points to.
    Raises:
        NotFoundException if no User entity is found"""
    user = User.query(User.name == username.title()).get()

    if not user:
        raise endpoints.NotFoundException(
            'User {} does not exist!'.format(username))
    else:
        return user


def get_player_by_game(username, game):
    """Returns an Player (ndb.Model) entity for a given username and game.
        First verify username and game entity are valid, raises error if not.
        Then returns the Player entity for the given user in the game.
        Raises an error if a Player is not found.
    Args:
        username: Username string
        game: Game ndb.Model entity
    Returns:
        The Player entity for a username in the given game.
    Raises:
        NotFoundException if no User entity is found from the given username.
        NotFoundException Game entity is not valid.
        NotFoundException if no Player entity is found."""

    # check to make sure User exists
    if not check_user_exists(username):
        raise endpoints.NotFoundException(
            '{} does not exist!'.format(username))

    # check to see if game is a valid Game entity
    if not isinstance(game, Game):
        raise endpoints.NotFoundException('Game not found')

    # check to see if Player is in this game
    player = Player.query(
        ancestor=game.key).filter(
        Player.name == username.title()).get()
    if not player:
        raise endpoints.NotFoundException(
            '{} is not in this game'.format(username))
    else:
        return player
