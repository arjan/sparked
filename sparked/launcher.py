# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
The sparked application launcher.

Sparked applications are launched in a subprocess: so that if the
application crashes, it is started again.
"""

import os
import subprocess
import sys
import tempfile
import time

from twisted.internet import reactor
from twisted.python import usage, log
from twisted.application import service, app

from sparked import application, __version__


class Options(usage.Options):

    longdesc = """The <application> argument specifies a Python module which is executed as the main sparked class. To see which options hold for an application, start:

# sparkd <application> --help
"""

    optFlags = [["debug", "d", "Debug mode"],
                ["no-subprocess", "N", "Do not start a subprocess for crash prevention"],
                ]

    optParameters = [
            ('id', None, None, 'Application id (defaults to the sparked module name)'),
            ('pidfile', None, None, 'Pidfile location (defaults to /tmp/<app-id>/sparkd.pid)'),
            ('logfile', None, None, 'Pidfile location (defaults to /tmp/<app-id>/sparkd.log)')
            ]


    def getSynopsis(self):
        return "sparkd [options] <application> [app_options]"

    def opt_version(self):
        print os.path.basename(sys.argv[0]), __version__
        exit(0)


class QuitFlag:
    """
    @ivar file: A C{FilePath} pointing to the quit-flag file.
    """
    def __init__(self, file):
        self.file = file


    def set(self):
        f = self.file.open("w")
        f.write("quit")
        f.close()


    def reset(self):
        try:
            self.file.remove()
        except:
            pass


    def isSet(self):
        try:
            return self.file.open("r").readlines()[0] == "quit"
        except:
            return False




def splitOptions(args):
    try:
        app = [a for a in args if a[0] != "-"][0]
    except IndexError:
        return args, None, []
    i = args.index(app)
    return (args[0:i], app, args[i+1:])


def run(appName):
    application = service.Application(appName)
    
    from sparked import tap
    config = tap.Options()
    config.parseOptions(sys.argv[1:])
    svc = tap.makeService(config)
    svc.setServiceParent(application)
        
    app.startApplication(application, False)
    log.addObserver(log.FileLogObserver(sys.stdout).emit)

    reactor.run()


def launch(baseOptions, env):
    argv = []
    argv.append("twistd")
    argv.append("--pidfile")
    argv.append(baseOptions['pidfile'])
    argv.append('-r')
    argv.append('gtk2')
    argv.append('-n')
    argv.append('sparked')
    argv = argv + sys.argv[1:]

    return subprocess.call(argv, env=env)


def launchLoop(app, options, env, appPath):
    quitFlag = QuitFlag(appPath.child("quitflag"))
    quitFlag.reset()
    respawned = False
    while True:
        start = time.time()
        launch(options, env)
        if time.time() - start < 5:
            if respawned:
                print "*** %s: respawning too fast ***" % app
            break
        if quitFlag.isSet():
            break
        respawned = True

    quitFlag.reset()



def loadModule(app):
    if app[-3:] == ".py" and os.path.exists(app):
        path = os.path.dirname(app)
        if not path: path = "."
        sys.path.insert(0, path)
        app = os.path.basename(app)[:-3]

    try:
        mod = __import__(app, None, None, app.split(".")[-1])
    except ImportError, e:
        log.err(e)
        raise usage.UsageError("Application not found: " + app)
    return mod, app



def main():

    env = os.environ

    try:
        options = Options()
        sparkedOpts, appName, appOpts = splitOptions(sys.argv[1:])
        options.parseOptions(sparkedOpts)

        if not appName:
            options.opt_help()

        appModule, appName = loadModule(appName)

        appPath = application.getTempPath(appName, options['id'])

        if hasattr(appModule, 'Options'):
            opts = appModule.Options()
        else:
            opts = application.Options()

        opts.appName = appName
        if not hasattr(opts, 'longdesc'):
            opts.longdesc = appModule.__doc__
        opts.parseOptions(appOpts)

        if not options['pidfile']:
            options['pidfile'] = appPath.child("sparkd.pid").path


        if options['no-subprocess']:
            run(appName)
        else:
            launchLoop(appName, options, env, appPath)


    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        sys.exit(1)


