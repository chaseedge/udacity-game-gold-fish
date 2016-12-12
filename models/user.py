from google.appengine.ext import ndb
from forms import ScoreForm

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=False)
    wins = ndb.IntegerProperty(default=0)
    losses = ndb.IntegerProperty(default=0)
    games = ndb.IntegerProperty(default=0)

    def to_form(self):
        """Returns a GameForm representation of the Game"""
        form = ScoreForm()

        form.name = self.name
        form.games = self.games
        form.wins = self.wins
        form.loses = self.loses

        return form
