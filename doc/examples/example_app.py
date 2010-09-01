# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Example runner class for sparked.
"""

from twisted.internet import reactor
from sparked import application

class Options(application.Options):
   optFlags = [["fast", "f", "Run fast"]]

__version__ = "0.1.0"


class Application(application.Application):

    title = "Spark example"

    def startService(self):
        application.Application.startService(self)

        if self.appOpts['fast']:
            self.delay = 1
        else:
            self.delay = 10

        from sparked.hardware.hal import SerialPortMonitor
        reactor.callLater(0, SerialPortMonitor().setServiceParent, self)

    def enter_start(self):
        self.state.setAfter("ping", self.delay)


    def enter_ping(self):
        self.state.setAfter("start", self.delay)


    def createStage(self):
        return False
