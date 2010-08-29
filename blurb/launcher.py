# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

import sys
import os
import tempfile
import subprocess

from twisted.python import usage

from blurb import application, __version__


class Options(usage.Options):

    optFlags = [["debug", "d", "Debug mode"]]

    optParameters = [
            ('pidfile', None, None, 'Pidfile location (defaults to /tmp/<application>.pid')
            ]


    def opt_version(self):
        print "Blurb", __version__

    def getSynopsis(self):
        return usage.Options.getSynopsis(self) + " <application> [app_options]"



def splitOptions(args):
    try:
        app = [a for a in args if a[0] != "-"][0]
    except IndexError:
        return args, None, []
    i = args.index(app)
    return (args[0:i], app, args[i+1:])


def launch(baseOptions):
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
        blurbOpts, app, appOpts = splitOptions(sys.argv[1:])
        options.parseOptions(blurbOpts)

        if not app:
            options.opt_help()

        try:
            appModule = __import__(app)
        except ImportError:
            raise usage.UsageError("Application not found: " + app)

        if getattr(appModule, 'Options'):
            opts = appModule.Options()
            opts.parseOptions(appOpts)

        appInstance = appModule.Application(options, opts)
        if not isinstance(appInstance, application.Application):
            raise usage.Usage("Invalid application module: " + appModule)

        if not options['pidfile']:
            options['pidfile'] = os.path.join(tempfile.gettempdir(), app + ".pid")

        launch(options)


    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        sys.exit(1)
