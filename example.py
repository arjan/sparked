# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.
#
# Example runner class for blurb.

from twisted.python import usage
from blurb import application

class Options(usage.Options):
    optFlags = [["fast", "f", "Run fast"]]


class Application(application.Application):

    title = "Blurb example"

    def startService(self):
        application.Application.startService(self)

        if self.appOpts['fast']:
            self.delay = 1
        else:
            self.delay = 10


    def enter_start(self):
        self.state.setAfter("ping", self.delay)


    def enter_ping(self):
        self.state.setAfter("start", self.delay)

