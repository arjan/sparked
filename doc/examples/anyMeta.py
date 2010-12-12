# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
An example that connects to an anymeta website.
"""

from twisted.python import log

from sparked import application
from sparked.internet import mediamatic

class Options(application.Options):
    optParameters = [
        ["api", None, None, "Anymeta API id"]
        ]

__version__ = "0.1.0"


class Application(application.Application):
    title = "Anymeta demo"


    def createMonitors(self):
        m = application.Application.createMonitors(self)
        # add the monitor. This will add an 'api' attribute to the Application.
        m.addMonitor(mediamatic.AnymetaAPIMonitor(self))
        return m

    def started(self):
        # use the 'api' attribute to get info on AnyMeta.
        self.api.anymeta.user.info().addCallback(log.msg)
