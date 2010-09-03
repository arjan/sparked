# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Example runner class for sparked.
"""

from sparked import application, monitors
from sparked.internet.zeroconf import zeroconfService

class Options(application.Options):
    optFlags = [["fast", "f", "Run fast"]]

__version__ = "0.1.0"


class Application(application.Application):

    title = "Spark example"
    
    def startService(self):
        application.Application.startService(self)
        
        zeroconfService.subscribeTo("_daap._tcp")
        
        if self.appOpts['fast']:
            self.delay = 1
        else:
            self.delay = 10
        zeroconfService.publishService("Test muziek2", "_daap._tcp", 3333)


    def enter_start(self):
        self.state.setAfter("ping", self.delay)


    def enter_ping(self):
        self.state.setAfter("start", self.delay)


    def createStage(self):
        return False


    def createMonitors(self):
        m = application.Application.createMonitors(self)

        m.addMonitor(monitors.NamedZeroconfMonitor("_daap._tcp", "Test muziek"))

        return m
