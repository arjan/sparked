# -*- test-case-name:  sparked.test.test_application -*-
# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
The base application class.
"""

import os
import signal
import time
import inspect

try:
    import json
except ImportError:
    import simplejson as json

from twisted.application import service
from twisted.python import log, usage, filepath

from sparked import monitors, events, __version__


class Application(service.MultiService):
    """
    The sparked base class.

    Spark applications inherit from this class.

    @ivar state: A L{StateMachine} instance which represents the main state of the Spark application.
    @ivar baseOpts: the basic options that are given on the sparked commandline; instance of L{sparked.launcher.Options}.
    @ivar appOpts: the additional applocation commandline options; instance of your application's C{yourapplication.Options}.
    @ivar quitFlag: A L{launcher.QuitFlag} instance controlling the clean shutdown of the program. Set by L{tap.makeService}.

    @ivar title:  The human-readable title of the application.

    @ivar monitors:      the L{monitors.MonitorContainer} instance with system monitors.
    @ivar statusWindow:  the status window with information about the applictaion.
    @ivar stage:         the stage for the display of graphics
    """

    state = None
    baseOpts = None
    appOpts = None
    quitFlag = None

    title = "Untitled"

    monitors = None
    statusWindow = None
    stage = None

    appName = None
    appId = None


    def __init__(self, appName, baseOpts, appOpts, reactor=None):
        service.MultiService.__init__(self)

        self.appName = appName
        self.baseOpts = baseOpts
        self.appOpts = appOpts
        self.appId = baseOpts.get('id', appName)

        if reactor is None:
            from twisted.internet import reactor
        self.reactor = reactor

        self.state = StateMachine(self, reactor)
        self.events = events.EventDispatcher()

        self.createMonitors()

        def doReload(prev):
            if callable(prev):
                prev()
            self.loadOptions()
            self.events.dispatch("signal-usr2")
        prevHandler = signal.getsignal(signal.SIGUSR2)
        signal.signal(signal.SIGUSR2, lambda sig, frame: doReload(prevHandler))

        def trap(f):
            try:
                f()
            except:
                log.err()
                self.reactor.stop()
        self.reactor.callLater(0, trap, self.starting)
        self.reactor.callLater(0, self.loadOptions, firstTime=True)
        self.reactor.callLater(0, self.state.set, "start")
        self.reactor.callLater(0, trap, self.started)


    def path(self, kind):
        """
        Return the path (a L{filepath.FilePath}) for this application
        for a given path kind. Kind is one of: temp, log, pid, share,
        data. The paths returned depend on the sys.prefix, the
        application path prefix, the appName and the application id.
        """
        return getPath(kind, self.appName, dict(self.baseOpts))


    def starting(self):
        """
        The application is starting. Add your event observers etc,
        etc, here.
        """


    def started(self):
        """
        The application has just been started and has entered the
        'start' state. Add your own services, create the stage, the
        status windows, etc, etc, here.
        """


    def createMonitors(self):
        m = monitors.MonitorContainer()
        m.addMonitor(monitors.PowerMonitor())
        m.addMonitor(monitors.NetworkMonitor())
        m.addMonitor(monitors.NetworkWebMonitor())

        # Make sure the monitors talk to us in the log.
        m.verbose = True

        self.reactor.callLater(0, m.setServiceParent, self)
        self.monitors = m
        return m


    def stopService(self):
        self.quitFlag.set()


    def loadOptions(self, firstTime=False):
        """
        Load options from options.json. Automatically called on
        application load and on on USR2 signal.
        """
        cfgfile = self.path("db").child("options.json")
        if not cfgfile.exists():
            if firstTime:
                self.events.dispatch("options-loaded", self.appOpts)
            return
        cls = self.appOpts.__class__
        try:
            newOpts = cls.load(cfgfile.path)
        except ValueError, e:
            print "** Syntax error in options.json **"
            log.err(e)
            return

        self.appOpts.update(newOpts)
        self.events.dispatch("options-loaded", self.appOpts)


    def saveOptions(self):
        """
        Save options from settings.json. Never called automatically.
        """
        self.appOpts.save(self.path("db").child("options.json").path)
        self.events.dispatch("options-saved", self.appOpts)


class Options (usage.Options):
    """
    Option parser for sparked applications.

    Spark applications which need their own commandline arguments can
    inherit from this class: it takes care of the --version and --help
    arguments, using the __version__ and docstring from the sparked
    application::

      # sparked example --version
      example 0.1.0 (sparked 0.1)

      # sparked example --help
      sparked [sparked options] example [options]
      Options:
         -f, --fast   Run fast
         --version
         --help       Display this help and exit.

      Example runner class for sparked.

    """

    appName = None
    def getSynopsis(self):
        return "sparked [sparked options] %s [options]" % self.appName

    def opt_version(self):
        if self.appName:
            m = __import__(self.appName)
            if hasattr(m, "__version__"):
                v = m.__version__+" "
            else:
                v = ""
            print "%s %s(sparked %s)" % (self.appName, v, __version__)
        exit(0)


    def save(self, fn):
        fp = open(fn, "w")
        fp.write(json.dumps(dict(self)))
        fp.close()


    def load(cls, fn):
        inst = cls()
        values = json.loads(open(fn, "r").read())
        inst.opts = values
        inst.update(values)
        for k,v in values.iteritems():
            if hasattr(inst, 'optParameters') and k in [l[0] for l in inst.optParameters if len(l)==5]:
                # check arg type
                tpe = [l for l in inst.optParameters if len(l)==5][0][4]
                if type(v) != tpe:
                    raise ValueError("Expected type '%s' for parameter '%s'" % (tpe, k))
            elif hasattr(inst, 'opt_%s' % k):
                f = getattr(inst, 'opt_%s' % k)
                if len(inspect.getargspec(f)[0]) == 1:
                    if v: f()
                else:
                    f(v)

        inst.postOptions()
        return inst
    load = classmethod(load)



def getPath(kind, appName, options):
    """
    Return the path (a L{filepath.FilePath}) for this application
    for a given path kind. Kind is one of: temp, log, pid, share,
    data. The paths returned depend on the sys.prefix, the
    application path prefix, the appName and the application id.
    """
    base = options.get("id") or appName
    if kind == "temp":
        return filepath.FilePath(os.path.expanduser(options.get("temp-path") or "/tmp/" + base))

    if kind == "logfile":
        if options.get("logfile"):
            return filepath.FilePath(os.path.expanduser(options.get("logfile")))
        if options.get("system-paths"):
            return filepath.FilePath("/var/log").child(base+".log")
        return getPath("temp", appName, options).child("sparkd.log")

    if kind == "pidfile":
        if options.get("pidfile"):
            return filepath.FilePath(os.path.expanduser(options.get("pidfile")))
        if options.get("system-paths"):
            return filepath.FilePath("/var/run").child(base+".pid")
        return getPath("temp", appName, options).child("sparkd.pid")

    if kind == "data":
        if options.get("data-path"):
            return filepath.FilePath(os.path.expanduser(options.get("data-path")))
        if options.get("system-paths"):
            return filepath.FilePath("/usr/share").child(appName)
        return filepath.FilePath("data/")

    if kind == "db":
        if options.get("db-path"):
            return filepath.FilePath(os.path.expanduser(options.get("db-path")))
        if options.get("system-paths"):
            return filepath.FilePath("/var/lib").child(base)
        return getPath("temp", appName, options).child("db")

    raise ValueError("Unknown path kind: " + kind)



class StateMachine (object):
    """
    A simple state machine.

    This machine is linked to a parent class, on which it calls
    enter_<state> and exit_<state> methods on state change. Also
    provided is a mechanism for timed state changes.

    @ivar nextStateAfter: nr of seconds after which the next state
    change is triggered. If None, the timer is not active.
    """

    _state = None
    _statechanger = None
    _listeners = None

    nextStateAfter = None


    def __init__(self, parent, reactor=None):
        self._listeners = []
        self.addListener(parent)
        if reactor is None:
            from twisted.internet import reactor
        self.reactor = reactor


    def set(self, newstate):
        """
        Sets a new state. Calls parent's state transition functions,
        if they exist.
        """

        if self._statechanger and self._statechanger.active():
            self._statechanger.cancel()
        self._statechanger = None
        self.nextStateAfter = None

        if self._state:
            self._call("exit_%s" % self._state, True)  # call reversed

        log.msg("%s --> %s" % (self._state, newstate))
        self._state = newstate

        self._call("enter_%s" % self._state)


    def setAfter(self, newstate, after):
        """
        Make a state transition after a specified amount of time.
        """
        self._afterStart = time.time()
        self._afterStop = self._afterStart + after
        self.nextStateAfter = after
        self._statechanger = self.reactor.callLater(after, self.set, newstate)


    def bumpAfter(self, after=None):
        """
        Change the state-changer timer to the specified nr of
        seconds. If none given, resets the timer to the initial delay,
        'bumping' it.
        """
        if not after:
            after = self.nextStateAfter
        self.nextStateAfter = after
        self._statechanger.reset(after)


    @property
    def get(self):
        """
        Get the current state.
        """
        return self._state


    def _call(self, cb, reverse=False):
        listeners = self._listeners
        if reverse:
            listeners = listeners[::-1]
        for l in listeners:
            try:
                getattr(l, cb)()
            except AttributeError:
                pass


    def addListener(self, l):
        self._listeners.append(l)
