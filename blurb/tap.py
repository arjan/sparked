# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

from twisted.application import service
from twisted.python import usage
from twisted.internet import reactor

from blurb import launcher, base


class Options(usage.Options):
    def parseOptions(self, o):
        blurbOpts, pluginName, pluginOpts = launcher.splitOptions(o)
        self.opts = launcher.Options()
        self.opts.parseOptions(blurbOpts)

        self.module = __import__(pluginName)
        self.pluginOpts = self.module.Options()
        self.pluginOpts.parseOptions(pluginOpts)


def makeService(config):
    s = config.module.Blurb(config.opts, config.pluginOpts)

    reactor.callLater(0, base.systemEvents.sendEvent, "started!")
    return s
