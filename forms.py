from protorpc import messages, message_types

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    game_over = messages.BooleanField(2, required=True)
    player1 = messages.StringField(3, required=True)
    player1_hand = messages.StringField(4,required=False)
    player1_matches = messages.IntegerField(5, required=False)
    player2 = messages.StringField(6, required=True)
    player2_hand = messages.StringField(7, required=False)
    player2_matches = messages.IntegerField(8, required=False)
    message = messages.StringField(9, required=True)
    turn = messages.StringField(10, required=False)
    winner = messages.StringField(11, required=False)
    started_on = message_types.DateTimeField(12, required=True)

class AllGames(messages.Message):
    """Returns all games"""
    games = messages.MessageField(GameForm, 1, repeated=True)

class UserGameForm(messages.Message):
    """UserGameForm for a user's game"""
    game_url = messages.StringField(1, required=True)
    opponent = messages.StringField(2, required=True)

class AllUserGames(messages.Message):
    """Return the key for all games for a given user"""
    games = messages.MessageField(UserGameForm, 1, repeated=True)

class GameScoreForm(messages.Message):
    """ScoreForm for a game"""
    game_url = messages.StringField(1, required=True)
    started_on = message_types.DateTimeField(2, required=True)
    player1 = messages.StringField(3, required=True)
    player1_matches = messages.IntegerField(4,required=False)
    player2 = messages.StringField(5, required=True)
    player2_matches = messages.IntegerField(6, required=False)
    turn = messages.IntegerField(7, required=False)
    winner = messages.StringField(8, required=False)
    game_over = messages.BooleanField(9, required=True)

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)

class AllUsersForm(messages.Message):
    """AllUsersForm returns list of all users"""
    users = messages.StringField(1, repeated=True)

class ScoreForm(messages.Message):
    """ScoreForm each entry"""
    player = messages.StringField(1, required=True)
    games = messages.IntegerField(2, required=True)
    wins = messages.IntegerField(3, required=True)
    loses = messages.IntegerField(4, required=True)

class ScoreBoard(messages.Message):
    """ScoreBoard form"""
    scores = messages.StringField(1, required=False, repeated=True)

class CancelGame(messages.Message):
    """CancelGame Response Form"""
    canceled = messages.StringField(1, required=True)
