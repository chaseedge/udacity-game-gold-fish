from protorpc import messages

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    game_over = messages.BooleanField(2, required=True)
    player_names = messages.StringField(3, repeated=True)
    message = messages.StringField(4, required=True)
    turn = messages.StringField(5, required=True)
    # player1 = messages.StringField(5, required=True)
    # player2 = messages.StringField(6, required=True)
    # player1_hand = messages.StringField(7, repeated=True)
    # player2_hand = messages.StringField(8, repeated=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    player1 = messages.StringField(1, required=True)
    player2 = messages.StringField(2, required=True)


# class MakeGuess(messages.Message):
#     """Used to make the Go Fish guess"""
#     urlsafe_key = messages.StringField(1, required=True)
#     player_name = messages.StringField(2,required=True)
#     player_guess = messages.StringField(3, required=True)

class MakeMoveForm(messages.Message):
    """Used to make a guess in an existing game"""
    player_name = messages.StringField(1, required=True)
    player_guess = messages.StringField(2, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    guesses = messages.IntegerField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)

