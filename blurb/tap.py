# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

from twisted.python import usage
from twisted.internet import reactor

from twisted.python import log
from twisted.python.filepath import FilePath
from twisted.python.logfile import LogFile

from blurb import launcher, base


class Options(usage.Options):
    def parseOptions(self, o):
        blurbOpts, pluginName, pluginOpts = launcher.splitOptions(o)
        self.opts = launcher.Options()
        self.opts.parseOptions(blurbOpts)

        self.pluginName = pluginName
        self.module = __import__(self.pluginName)

        if getattr(self.module, 'Options'):
            self.pluginOpts = self.module.Options()
            self.pluginOpts.parseOptions(pluginOpts)
        else:
            self.pluginOpts = usage.Options()


def makeService(config):
    s = config.module.Blurb(config.opts, config.pluginOpts)

    # Set up logging in ~/log/ikpoll.log, maximum 9 rotated log files.
    import tempfile

    if not config.opts['debug']:
        logDir = FilePath(tempfile.gettempdir()).child('log')
        if not logDir.exists():
            logDir.createDirectory()
        logfile = config.pluginName.replace(".", "_") + ".log"
        logFile = LogFile(logfile, logDir.path, maxRotatedFiles=9)
        log.addObserver(log.FileLogObserver(logFile).emit)

    reactor.callLater(0, base.systemEvents.sendEvent, "started!")
    return s
