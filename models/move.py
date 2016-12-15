from datetime import datetime
from google.appengine.ext import ndb

from forms import GameHistoryForm


class Move(ndb.Model):
    """Move object for guesses in a game"""
    player = ndb.KeyProperty(required=True, kind='Player')
    name = ndb.StringProperty(required=True)
    time = ndb.DateTimeProperty(required=True, default=datetime.now())
    guess = ndb.StringProperty(required=True)
    match = ndb.BooleanProperty(required=True)
    game_over = ndb.BooleanProperty(required=True)
    message = ndb.StringProperty(required=False)

    def to_form(self):
        """Returns move into GameHistoryForm"""
        form = GameHistoryForm()
        form.time = self.time
        form.player = self.name
        form.guess = self.guess
        form.match = self.match
        form.game_over = self.game_over

        return form
