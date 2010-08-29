# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
The spark application launcher.

Spark applications are launched in a subprocess: so that if the
application crashes, it is started again.
"""

import os
import subprocess
import sys
import tempfile
import time

from twisted.python import usage

from spark import __version__


class Options(usage.Options):

    optFlags = [["debug", "d", "Debug mode"],
                ["no-respawn", "N", "Do not respawn on crash"],
                ]

    optParameters = [
            ('pidfile', None, None, 'Pidfile location (defaults to /tmp/<application>.pid')
            ]


    def opt_version(self):
        print "spark", __version__

    def getSynopsis(self):
        return usage.Options.getSynopsis(self) + " <application> [app_options]"



class QuitFlag:

    def __init__(self, app):
        self.file = os.path.join(tempfile.gettempdir(), app+".quit")


    def set(self):
        f = open(self.file, "w")
        f.write("quit")
        f.close()


    def reset(self):
        try:
            os.unlink(self.file)
        except:
            pass


    def isSet(self):
        try:
            return open(self.file, "r").readlines()[0] == "quit"
        except:
            return False




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
    argv.append('spark')
    argv = argv + sys.argv[1:]

    env = os.environ
    return subprocess.call(argv, env=env)


def launchLoop(app, options):
    quitFlag = QuitFlag(app)
    quitFlag.reset()
    respawned = False
    while True:
        start = time.time()
        launch(options)
        if time.time() - start < 5:
            if respawned:
                print "*** %s: respawning too fast ***" % app
            break
        if quitFlag.isSet():
            break
        respawned = True

    quitFlag.reset()



def main():

    try:

        options = Options()
        sparkOpts, app, appOpts = splitOptions(sys.argv[1:])
        options.parseOptions(sparkOpts)

        if not app:
            options.opt_help()

        try:
            appModule = __import__(app)
        except ImportError:
            raise usage.UsageError("Application not found: " + app)

        if hasattr(appModule, 'Options'):
            opts = appModule.Options()
            opts.parseOptions(appOpts)

        if not options['pidfile']:
            options['pidfile'] = os.path.join(tempfile.gettempdir(), app + ".pid")


        if options['no-respawn']:
            launch(options)
        else:
            launchLoop(app, options)


    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        sys.exit(1)


