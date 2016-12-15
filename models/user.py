from google.appengine.ext import ndb

from forms import UserScoreForm


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=False)
    wins = ndb.IntegerProperty(default=0)
    losses = ndb.IntegerProperty(default=0)
    games_behind = ndb.IntegerProperty(default=0)
    games = ndb.IntegerProperty(default=0)
    win_ratio = ndb.FloatProperty(default=0)

    # scoreboard output
    def to_form(self):
        """Returns Users results - all completed games, wins and losses"""
        form = UserScoreForm()
        form.player = self.name
        form.games_played = self.games
        form.wins = self.wins
        form.losses = self.losses
        form.win_ratio = self.win_ratio

        return form
