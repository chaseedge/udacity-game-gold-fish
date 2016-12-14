from protorpc import messages, message_types


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    game_over = messages.BooleanField(2, required=True)
    player1 = messages.StringField(3, required=True)
    player1_hand = messages.StringField(4, required=False)
    player1_matches = messages.IntegerField(5, required=False)
    player2 = messages.StringField(6, required=True)
    player2_hand = messages.StringField(7, required=False)
    player2_matches = messages.IntegerField(8, required=False)
    message = messages.StringField(9, required=True)
    turn = messages.StringField(10, required=False)
    winner = messages.StringField(11, required=False)
    started_on = message_types.DateTimeField(12, required=True)


class AllGamesForm(messages.Message):
    """Returns all games data"""
    games = messages.MessageField(GameForm, 1, repeated=True)


class UserGameForm(messages.Message):
    """UserGameForm for a user's game"""
    game_url = messages.StringField(1, required=True)
    opponent = messages.StringField(2, required=True)


class AllUserGamesForm(messages.Message):
    """Return the key for all games for a given user"""
    games = messages.MessageField(UserGameForm, 1, repeated=True)


class MoveForm(messages.Message):
    """MoveForm response for a players guess"""
    message = messages.StringField(1, required=True)
    match = messages.BooleanField(2, required=False)
    hand = messages.StringField(3, required=False)
    num_matches = messages.IntegerField(4, required=False)
    game_over = messages.BooleanField(5, required=True)


class PlayerHandForm(messages.Message):
    """PlayerHandForm returns hand and matches"""
    message = messages.StringField(1, required=False)
    hand = messages.StringField(2, required=False)
    matches = messages.StringField(3, required=False)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)


class StringRepeatedMessage(messages.Message):
    """StringMessage-- outbound (multiple) string messages"""
    messages = messages.StringField(1, repeated=True)
