#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.ext import ndb
from google.appengine.api import mail, app_identity
from api import GoFishApi

from models.user import User
from models.game import Game


class SendReminderEmail(webapp2.RequestHandler):

    def get(self):
        """Send a reminder email to each User with an email about games.
        Called every hour using a cron job"""
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)

        # check to see if any users have emails
        if users.count() >= 1:
            for user in users:

                # retrieve games of the player that are not over
                game = Game.query(ndb.AND(Game.game_over == False,
                                          Game.player_names.IN([user.name])))

                if game.count() > 0:
                    subject = 'This is a reminder that you have an active game!'
                    body = 'Hello {}, you have an active game going!'.format(
                        user.name)
                    
                    # This will send test emails, the arguments to send_mail are:
                    # from, to, subject, body
                    mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                                   user.email,
                                   subject,
                                   body)


class UpdateScoreboard(webapp2.RequestHandler):

    def post(self):
        """Update game listing announcement in memcache."""
        GoFishApi._cache_scoreboard()
        self.response.set_status(204)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/cache_scoreboard', UpdateScoreboard),
], debug=True)
