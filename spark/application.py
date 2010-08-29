# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
The base application class.
"""

import time

from twisted.application import service
from twisted.python import log, usage
from twisted.internet import reactor

from spark import gui, stage, monitors, __version__


class Application(service.MultiService):
    """
    The spark base class.

    Spark applications inherit from this class.

    @ivar state: A L{StateMachine} instance which represents the main state of the Spark application.
    @ivar baseOpts: the basic options that are given on the spark commandline; instance of L{spark.launcher.Options}.
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


    def __init__(self, baseOpts, appOpts):
        service.MultiService.__init__(self)

        self.baseOpts = baseOpts
        self.appOpts = appOpts

        self.state = StateMachine(self)

        reactor.callLater(0, self.startUp)
        reactor.callLater(0, self.state.set, "start")


    def startUp(self):
        """
        Create all services and GUI objects as needed.
        """

        self.monitors = self.createMonitors()

        self.statusWindow = self.createStatusWindow()

        self.stage = self.createStage()


    def createStatusWindow(self):
        """
        Create the status window

        If your application does not need a status window, override
        this method in your application's subclass and return
        C{False}. This removes the dependency on the C{gtk} library.
        """
        gui.guiEvents.addEventListener(lambda _: reactor.stop(), gui.StatusWindowClosed)
        return gui.StatusWindow(self)


    def createStage(self):
        """
        Create the graphics stage.

        If your application does not need a graphics stage, override
        this method in your application's subclass and return
        C{False}. This removes the dependency on the C{clutter} library.
        """
        s = stage.Stage(self)
        if not self.baseOpts['debug']:
            s.toggleFullscreen()
        stage.stageEvents.addEventListener(lambda _: reactor.stop(), stage.StageClosed)
        return s


    def createMonitors(self):
        m = monitors.MonitorContainer()
        m.addMonitor(monitors.PowerMonitor())
        m.addMonitor(monitors.NetworkMonitor())
        m.addMonitor(monitors.NetworkWebMonitor())

        m.setServiceParent(self)
        return m


    def stopService(self):
        self.quitFlag.set()



class Options (usage.Options):
    """
    Option parser for spark applications.

    Spark applications which need their own commandline arguments can
    inherit from this class: it takes care of the --version and --help
    arguments, using the __version__ and docstring from the spark
    application::

      # spark example --version
      example 0.1.0 (spark 0.1)

      # spark example --help
      spark [spark options] example [options]
      Options:
         -f, --fast   Run fast
         --version
         --help       Display this help and exit.

      Example runner class for spark.

    """

    appName = None
    def getSynopsis(self):
        return "spark [spark options] %s [options]" % self.appName

    def opt_version(self):
        if self.appName:
            m = __import__(self.appName)
            if hasattr(m, "__version__"):
                v = m.__version__
            else:
                v = ""
            print "%s %s (spark %s)" % (self.appName, v, __version__)
        exit(0)



class StateMachine (object):
    """
    A simple state machine.

    This machine is linked to a parent class, on which it calls
    enter_<state> and exit_<state> methods on state change. Also
    provided is a mechanism for timed state changes.
    """

    _state = None
    _statechanger = None
    _listeners = None


    def __init__(self, parent):
        self._listeners = []
        self.addListener(parent)


    def set(self, newstate):
        """
        Sets a new state. Calls parent's state transition functions,
        if they exist.
        """

        if self._statechanger and self._statechanger.active():
            self._statechanger.cancel()

        if self._state:
            self._call("exit_%s" % self._state)

        log.msg("%s --> %s" % (self._state, newstate))
        self._state = newstate

        self._call("enter_%s" % self._state)


    def setAfter(self, newstate, after):
        """
        Make a state transition after a specified amount of time.
        """
        self._afterStart = time.time()
        self._afterStop = self._afterStart + after
        self.next_state_after = after
        self._statechanger = reactor.callLater(after, self.set, newstate)


    @property
    def get(self):
        """
        Get the current state.
        """
        return self._state


    def _call(self, cb, *arg):
        for l in self._listeners:
            try:
                getattr(l, cb)(*arg)
            except AttributeError:
                pass


    def addListener(self, l):
        self._listeners.append(l)
