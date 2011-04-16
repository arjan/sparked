# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.
# -*- test-case-name:  sparked.test.test_launcher -*-

"""
The Sparked application launcher.

Sparked applications are launched in a subprocess: so that if the
application crashes, it is started again.
"""

import os
import subprocess
import sys
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
                ["system-paths", "s", """Setup the application paths so that the app is run as a
                system-wide application. The paths are according to the Filesystem Hierarchy Standard:
                respectively /tmp/<id>/; /var/log/<id>.log; /var/run/<id>.pid; /usr/share/<application>/; /var/lib/<id>/.
                """],
                ]

    optParameters = [
            ('id', None, None, 'Application instance id (defaults to <application>)'),
            ('temp-path', None, None, 'Temporary path (defaults to /tmp/<id>/'),
            ('logfile', None, None, 'Logfile. Defaults to <temp-path>/sparkd.log'),
            ('pidfile', None, None, 'Process-id file. Defaults to <temp-path>/sparkd.pid'),
            ('data-path', None, None, """Path where static application data is stored, like image files. Defaults to the "data" subdirectory of the current directory."""),
            ('db-path', None, None, """Path where instance-specific data is stored, like database files. Defaults to <temp-path>/db/"""),
            ]


    def getSynopsis(self):
        return "sparkd [options] <application> ..."

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


def runInSubprocess(app, options, env, tempPath):
    quitFlag = QuitFlag(tempPath.child("quitflag"))
    quitFlag.reset()
    respawned = False
    while True:
        start = time.time()

        argv = ["twistd", "--pidfile", options['pidfile'], '-r', 'gtk2', '-n', 'sparked'] + sys.argv[1:]
        subprocess.call(argv, env=env)

        if time.time() - start < 5:
            if respawned:
                sys.stderr.write("*** %s: respawning too fast ***\n" % app)
            break
        if quitFlag.isSet():
            break
        respawned = True

    quitFlag.reset()


def loadModule(app):
    """
    Given an module or python file, load the module. Returns a tuple
    containing the loaded module and the name of the app.
    """
    if hasattr(os, "getuid") and os.getuid() != 0:
        sys.path.insert(0, os.path.abspath(os.getcwd()))
    args = sys.argv[:]
    sys.argv = []
    if app[-3:] == ".py" and os.path.exists(app):
        path = os.path.dirname(app)
        if not path: path = "."
        sys.path.insert(0, path)
        from twisted.python import reflect
        app = reflect.filenameToModuleName(app)
    try:
        mod = __import__(app, None, None, app.split(".")[-1])
    except ImportError:
        sys.argv = args
        raise usage.UsageError("Application not found: " + app)
    sys.argv = args
    return mod, app


def launchHelp(app):
    print "This file is a Sparked application, and is meant to run like this:"
    print
    print " sparkd " + app
    print
    exit(1)



def launchApplication(argv):
    options = Options()
    sparkedOpts, appName, appOpts = splitOptions(argv)
    options.parseOptions(sparkedOpts)

    if not appName:
        raise usage.UsageError("Missing application name")

    appModule, appName = loadModule(appName)

    if hasattr(appModule, 'Options'):
        opts = appModule.Options()
    else:
        opts = application.Options()

    opts.appName = appName
    if not hasattr(opts, 'longdesc'):
        opts.longdesc = appModule.__doc__
    opts.parseOptions(appOpts)

    if options['no-subprocess']:
        return run(appName)

    options['pidfile'] = application.getPath('pidfile', appName, opts).path
    tempPath = application.getPath("temp", appName, opts)
    return runInSubprocess(appName, options, os.environ, tempPath)


def main():
    try:
        launchApplication(sys.argv[1:])
    except usage.UsageError, errortext:
        print 'sparkd: %s' % errortext
        print
        print 'Try sparkd --help for usage details.'
        print
        sys.exit(1)


