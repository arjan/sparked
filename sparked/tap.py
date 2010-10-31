# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Twisted Application Persistence package for the startup of the twisted sparked plugin.
"""

import tempfile
import dbus.mainloop.glib

from twisted.python import usage

from twisted.python import log
from twisted.python.filepath import FilePath
from twisted.python.logfile import LogFile

from sparked import launcher, application


class Options(usage.Options):
    def parseOptions(self, o):
        sparkedOpts, self.appName, appOpts = launcher.splitOptions(o)
        self.opts = launcher.Options()
        self.opts.parseOptions(sparkedOpts)

        if not self.appName:
            self.opts.opt_help()

        self.module, self.appName = launcher.loadModule(self.appName)

        if hasattr(self.module, 'Options'):
            self.appOpts = self.module.Options()
        else:
            self.appOpts = application.Options()
        self.appOpts.parseOptions(appOpts)



def makeService(config):

    # Create dbus mainloop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    # Check if it is the right thing
    if not hasattr(config.module, 'Application'):
        raise usage.UsageError("Invalid application module: " + config.appName)

    # Instantiate the main application
    s = config.module.Application(config.opts, config.appOpts)

    # Assign appliation name
    s.appName = config.appName
    # Assign the 'application id'
    s.id = config.opts['id']
    # Asign the containment path (if any)
    s.containPath = config.opts['contain-path']

    # Set quitflag 
    s.quitFlag = launcher.QuitFlag(s.path("temp").child("quitflag"))

    # Set the name
    s.setName(config.appName)

    # Set up logging in /tmp/log, maximum 9 rotated log files.
    logFile = s.path("log")
    if not logFile.parent().exists():
        logFile.parent().createDirectory()
    logFile = LogFile.fromFullPath(s.path("log").path, maxRotatedFiles=9)
    log.addObserver(log.FileLogObserver(logFile).emit)

    return s
