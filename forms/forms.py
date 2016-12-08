from protorpc import messages

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    game_over = messages.BooleanField(2, required=True)
    player_names = messages.StringField(3, repeated=True)
    message = messages.StringField(4, required=True)
    turn = messages.StringField(5, required=False)
    winner = messages.StringField(6, required=False)
    loser = messages.StringField(7, required=False)

class AllGames(messages.Message):
    """Returns all games"""
    games = messages.MessageField(GameForm, 1, repeated=True)

# class GameScore(messages.Message):
#     """ScoreForm for outbound Score information"""
#     datetime = messages.StringField(1, required=True)
#     player1 = messages.StringField(2, required=True)
#     player1_matches = messages.IntegerField(3, required=True)
#     player2 = messages.StringField(4, required=True)
#     player2_matches = messages.IntegerField(5, required=True)
#     game_over = messages.BooleanField(6, required=True)
#     winner = messages.BooleanField(7, required=True)
#
#
# class ScoreForms(messages.Message):
#     """Return multiple ScoreForms"""
#     items = messages.MessageField(ScoreForm, 1, repeated=True)

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)

class AllUsersForm(messages.Message):
    """AllUsersForm returns list of all users"""
    users = messages.StringField(1, repeated=True)
