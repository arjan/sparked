# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

import sys
import cPickle
import base64
import os
import tempfile
import subprocess

from twisted.python import usage

from blurb import base, __version__


class Options(usage.Options):

    optFlags = [["debug", "d", "Debug mode"]]

    optParameters = [
            ('pidfile', None, None, 'Pidfile location (defaults to /tmp/<pluginname>.pid')
            ]


    def opt_version(self):
        print "Blurb", __version__

    def getSynopsis(self):
        return usage.Options.getSynopsis(self) + " <plugin> [plugin_options]"



def splitOptions(args):
    try:
        plugin = [a for a in args if a[0] != "-"][0]
    except IndexError:
        return args, None, []
    i = args.index(plugin)
    return (args[0:i], plugin, args[i+1:])


def launch(pluginName, baseOptions):
    argv = []
    argv.append("twistd")
    argv.append("--pidfile")
    argv.append(baseOptions['pidfile'])
    argv.append('-r')
    argv.append('gtk2')
    argv.append('-n')
    argv.append('blurb')
    argv = argv + sys.argv[1:]

    env = os.environ
    return subprocess.call(argv, env=env)


def main():

    try:

        options = Options()
        blurbOpts, pluginName, pluginOpts = splitOptions(sys.argv[1:])
        options.parseOptions(blurbOpts)

        if not pluginName:
            options.opt_help()

        try:
            pluginModule = __import__(pluginName)
        except ImportError:
            raise usage.UsageError("Plugin not found: " + pluginName)

        if getattr(pluginModule, 'Options'):
            opts = pluginModule.Options()
            opts.parseOptions(pluginOpts)

        pluginInstance = pluginModule.Blurb(options, opts)
        if not isinstance(pluginInstance, base.Blurb):
            raise usage.Usage("Invalid blurb plugin module: " + pluginModule)

        if not options['pidfile']:
            options['pidfile'] = os.path.join(tempfile.gettempdir(), pluginName.replace(".", "_") + ".pid")

        launch(pluginName, options)


    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        sys.exit(1)
