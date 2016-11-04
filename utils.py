"""utils.py - File for collecting general utility functions."""

import logging
from google.appengine.ext import ndb
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



def check_player_exists(name):
    player = User.query(User.name == name).get()
    if not player:
        raise endpoints.NotFoundException(
            'Player {} does not exist!'.format(name))
    else:
        return player


def check_game_player(name, game_url, model):
    game = get_by_urlsafe(game_url, model)
    player = User.query(User.name == name).get()

    if not player:
        raise endpoints.NotFoundException(
            '{} does not exist!'.format(name))

    elif player.key == game.player1:
        print "player1"
        return game.player1_hand

    elif player.key == game.player2:
        print "player2"
        return game.player2_hand

    else:
        raise endpoints.NotFoundException(
            '{} is not in this game'.format(name))
        return False


