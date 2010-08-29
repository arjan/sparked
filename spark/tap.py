# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Twisted Application Persistence package for the startup of the twisted spark plugin.
"""

import tempfile
import dbus.mainloop.glib

from twisted.python import usage

from twisted.python import log
from twisted.python.filepath import FilePath
from twisted.python.logfile import LogFile

from spark import launcher, application


class Options(usage.Options):
    def parseOptions(self, o):
        sparkOpts, appName, appOpts = launcher.splitOptions(o)
        self.opts = launcher.Options()
        self.opts.parseOptions(sparkOpts)

        self.appName = launcher.getModule(appName)
        self.module = __import__(self.appName)

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

    # Set quitflag 
    s.quitFlag = launcher.QuitFlag(config.appName)

    # Set the name
    s.setName(config.appName)

    # Set up logging in /tmp/log, maximum 9 rotated log files.
    if not config.opts['debug']:
        logDir = FilePath(tempfile.gettempdir()).child('log')
        if not logDir.exists():
            logDir.createDirectory()
        logfile = config.appName + ".log"
        logFile = LogFile(logfile, logDir.path, maxRotatedFiles=9)
        log.addObserver(log.FileLogObserver(logFile).emit)

    return s
