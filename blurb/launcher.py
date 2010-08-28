# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

import sys

from twisted.python import usage

from blurb import __version__


class Options(usage.Options):

    optFlags = [["debug", "d", "Debug mode"]]

    def opt_version(self):
        print "Blurb", __version__

    def getSynopsis(self):
        return usage.Options.getSynopsis(self) + " <plugin> [plugin_options]"



def splitOptions():
    args = sys.argv[1:]
    try:
        plugin = [a for a in args if a[0] != "-"][0]
    except IndexError:
        return args, None, []
    i = args.index(plugin)
    return (args[0:i], plugin, args[i+1:])


def main():

    try:

        options = Options()
        blurbOpts, pluginName, pluginOpts = splitOptions()
        options.parseOptions(blurbOpts)

        if not pluginName:
            options.opt_help()

        try:
            pluginModule = __import__(pluginName)
        except ImportError:
            raise usage.UsageError("Plugin not found: " + pluginName)

        print pluginModule



    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        sys.exit(1)
