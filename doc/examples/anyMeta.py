# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
An example that connects to an anymeta website.
"""

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
        m.addMonitor(mediamatic.AnymetaAPIMonitor(self))
        return m

