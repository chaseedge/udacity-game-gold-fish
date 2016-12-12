from google.appengine.ext import ndb
from forms import UserGameForm

class Player(ndb.Model):
    """Creates players for the game"""
    user = ndb.KeyProperty(required=True, kind='User')
    name = ndb.StringProperty(required=True)
    opponent = ndb.StringProperty(required=True)
    game_url = ndb.StringProperty(required=True)
    hand = ndb.JsonProperty()
    num_matches = ndb.IntegerProperty(required=True, default=0)
    matches = ndb.JsonProperty(default=[])

    def check_pairs(self):
        temp_list = []
        message = "Following cards were paired for {}: ".format(self.name)
        for index, card in enumerate(self.hand):
            value_list = [x['rank'] for x in self.hand]

            if card['rank'] in temp_list:
                self.matches.append(card)
                self.hand.remove(card)
                temp_list.remove(card['rank'])
                message += " and {}".format(card['suit'])
                self.num_matches += 1

            if card['rank'] in value_list[index+1:]:
                self.matches.append(card)
                temp_list.append(card['rank'])
                message += "{} of {}".format(card['rank'], card['suit'])
                self.hand.remove(card)

        self.put()



    def check_game_over(self, matches):
        """Checks if the player is out of cards or has number of matches"""
        if len(self.hand) == 0 or len(self.matches)/2 >= matches:
            return True
        else:
            return False

    def to_form(self):
        """Returns game info for a given player"""
        form = UserGameForm()

        form.opponent = self.opponent
        form.game_url = self.game_url

        return form
