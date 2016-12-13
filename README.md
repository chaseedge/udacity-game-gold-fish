#Full Stack Nanodegree Project 4

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.



##Game Description:
Go Fish is the classic card game. Users register and are able to challenge
other users to the game. Each game begins with two players. Players
are dealt a certain number of cards (default is 5). Each player will take turns
asking for cards from the other player with the goal being get matches. Player
guesses are sent to the 'make_move' endpoint
which checks the other players hand for the guessed card.

The game is played until a player runs out of cards or gets a target number of
matches (default is 6). Set cards_dealt to a high number (e.g. 10) and
matches_to_win (e.g. 2) for games to go faster.

Many different Go Fish games can be played by many different Users at any
given time, but Users can only have one active game against each other User at
at any given time. Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

Uses memcache to update User's scores.

Game has a bias towards whoever goes first.

##Scoring
The game is over when the first player runs out of cards or reaches the target
number of matches.
The scoreboard shows users rankings and is sorted by wins.

##ToDo List:
- Implement tie feature
- Change scoreboard to a win ratio (currently number of wins behind 1st)


##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string
    and username
 - forms.py: Contains all response message forms
 - ** Models **
    - game.py: ndb Model for each game including helper methods.
    - user.py: ndb Model for users
    - player.py: ndb Model for each player of a game. Parent is a game


##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: username, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. username provided must be unique. Will
    raise a ConflictException if a User with that username already exists.

 - **get_all_users**
    - Path: 'user/all'
    - Method: GET
    - Parameters: NONE
    - Returns: Repeated string message of all users
    - Description: Returns all users and will raise NotFoundException if there are no users registered.

 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: player1, player2, cards_dealt, matches_to_win
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. Player1 and player2 must be
      valid existing usernames - will raise a NotFoundException if not.
      If players already have an active game between them, that game will
      be returned.
      The number of cards dealt to each player and the number of matches need
      to win can be set.
      Default cards dealt is 5 and matches to win is 6.
      Also adds a task to a task queue to update the scoreboard.

 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
      Raises NotFoundException if urlsafe_game_key is not valid.

 - **get_user_games**
    - Path: 'user/{username}'
    - Method: GET
    - Parameters: username
    - Returns: Returns AllUserGames that includes opponent name and
      urlsafe_game_key.
    - Description: Returns all games for a given username.
      Raises NotFoundException if username is not vaild or user has no games.

 - **get_all_game**
    - Path: 'games'
    - Method: GET
    - Parameters: active_only (optional)
    - Returns: GameForm with the current state of all games.
    - Description: Returns the state of all games or just active games.
      Raises NotFoundException if no games found.

 - **cancel_game**
    - Path: 'game/{urlsafe_game_key}/cancel'
    - Method: POST
    - Parameters: urlsafe_game_key, cancel (boolean)
    - Returns: StringMessage confirmation of game and associated players deleted.
    - Description: Deletes a game and associated players if game is not over,
      a valid urlsafe_game_key is provided and cancel is confirmed.
      Raises NotFoundException if invalid urlsafe_game_key
      Returns StringMessage if game is already over or cancel is not confirmed.

 - **get_player_hand**
    - Path: 'game/{urlsafe_game_key}/{username}/hand'
    - Method: GET
    - Parameters: urlsafe_game_key, username
    - Returns: PlayerHandForm with player's hand and matches.
    - Description: Returns a players hand from a given game. If game is over,
      'Game over' StringMessage is returned. Raises a NotFoundException if
      invalid urlsafe_game_key or if given player is not found in game.

 - **make_move**
    - Path: 'game/{urlsafe_game_key}/{username}/move'
    - Method: PUT
    - Parameters: urlsafe_game_key, username, guess
    - Returns: MakeMoveForm with result of guess, status of game, player hand
      and matches.
    - Description: Accepts a 'guess' and returns the updated state of the game.
      If this causes a game to end, a corresponding message will be returned.
      Raises a NotFoundException if invalid urlsafe_game_key or if given player
      is not found in game.

 - **get_game_history**
    - Path: 'game/{urlsafe_game_key}/{username}/history'
    - Method: GET
    - Parameters: urlsafe_game_key, username
    - Returns: StringRepeatedMessage of user guesses.
    - Description: Returns all of a users guesses for a given game. Raises a NotFoundException if invalid urlsafe_game_key or user not in game.

 - **get_user_rankings**
    - Path: 'games/scoreboard'
    - Method: GET
    - Parameters: None
    - Returns: StringRepeatedMessage of users and their records sorted by wins.
    - Description: Returns a leader board of all users scores sorted by wins

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.

 - **Game**
    - Stores unique game states.

 - **Player**
    - Stores a player for each user in a game with player's hand and matches. Associated with User model via KeyProperty and ancestor is the game.


##Outbound Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key,
    game_over flag, player1, player1_hand, player1_matches, player2, player2_hand, player2_matches, turn, winner, started_on, message).
 - **AllGamesForm**
    - Multiple GameForm container
 - **UserGameForm**
    - Brief representation of all users games. Includes urlsafe_game_key and opponent
 - **AllUserGamesForm**
    - Multiple UserGameForm container
 - **MoveForm**
    - Representation of the result from a player's guess (message, match flag, hand, matches, game_over flag)
 - **PlayerHandForm**
    - Representation of a players hand (message, hand, matches)
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.
 - **StringRepeatedMessage**
    - General purpose repeated String container

##Inbound Forms Included:
 - **NEW_GAME_REQUEST**
    - For new game (player1, player2, cards_dealt, matches_to_win)
 - **USER_GAMES_REQUEST**
    - To get all games for a given user (username)
 - **GET_GAME_REQUEST**
    - To get game by url (urlsafe_game_key)
 - **GET_ALL_GAMES_REQUEST**
    - To get all games, optional active only (active_only)
 - **CANCEL_GAME_REQUEST**
    - To cancel game, takes url and confirmation boolean (urlsafe_game_key, cancel)
 - **HAND_REQUEST**
    - To get players hand for a game (urlsafe_game_key, username)
 - **USER_REQUEST**
    - To create new user (username, email)
 - **MAKE_MOVE_REQUEST**
    - To make a move for a given game (urlsafe_game_key, username, guess)
 - **GAME_HISTORY_REQUEST**
    - To get a players guesses for a given game (username, urlsafe_game_key)
