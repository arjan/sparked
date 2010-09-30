# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
A simple example runner class for Sparked. It publishes a zeroconf
service, 'Test service', and creates a monitor which checks if this
'Test service' is available (normally, you would do that in a second,
'client' app.

The apps state machine 'pingpongs' between 'start' <-> 'ping'. There
is a commandline option which lets this pingponging go faster.

Try sparkd example_app.py --help to view the generated usage options
for this app.
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

        if self.appOpts['fast']:
            self.delay = 1
        else:
            self.delay = 10
        zeroconfService.publishService("Test service", "_daap._tcp", 3333)


    def enter_start(self):
        self.state.setAfter("ping", self.delay)


    def enter_ping(self):
        self.state.setAfter("start", self.delay)


    def createMonitors(self):
        m = application.Application.createMonitors(self)
        m.addMonitor(monitors.NamedZeroconfMonitor("Test service", "_daap._tcp"))
        return m
