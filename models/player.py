from google.appengine.ext import ndb
from forms import UserGameForm


class Player(ndb.Model):
    """Creates players for the game"""
    user = ndb.KeyProperty(required=True, kind='User')
    name = ndb.StringProperty(required=True)
    opponent = ndb.StringProperty(required=True)
    game_url = ndb.StringProperty(required=True)
    hand = ndb.JsonProperty()
    history = ndb.StringProperty(repeated=True)
    num_matches = ndb.IntegerProperty(required=True, default=0)
    matches = ndb.JsonProperty(default=[])

    def check_pairs(self):
        """Check for matches in hand"""

        # build index of matches
        matches_index = []
        for index, card in enumerate(self.hand):

            # List of all values in hand
            value_list = [x['rank'] for x in self.hand]

            # list of rest of cards values in hand
            temp_list = value_list[index + 1:]

            # check to see if the matched card is already in index
            if index not in matches_index:

                try:
                    match = temp_list.index(card['rank']) + index + 1
                    matches_index.append(index)
                    matches_index.append(match)

                except:
                    pass

        # sort high to low so matches can be removed and not change index
        matches_index.sort(reverse=True)

        self.num_matches += len(matches_index) / 2

        for x in matches_index:
            card = self.hand[x]

            # remove card from hand and add it to matches
            self.matches.append(card)
            self.hand.remove(card)

        self.put()

    def check_game_over(self, matches):
        """Checks if the player is out of cards or has number of matches"""
        if len(self.hand) == 0 or self.num_matches >= matches:
            return True
        else:
            return False

    def to_form(self):
        """Returns game info for a given player"""
        form = UserGameForm()

        form.opponent = self.opponent
        form.game_url = self.game_url

        return form
