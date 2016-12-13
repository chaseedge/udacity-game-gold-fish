from google.appengine.ext import ndb
from forms import ScoreForm


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=False)
    wins = ndb.IntegerProperty(default=0)
    losses = ndb.IntegerProperty(default=0)
    games_behind = ndb.IntegerProperty(default=0)
    games = ndb.IntegerProperty(default=0)
