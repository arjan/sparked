# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
The base application class.
"""

import time
import tempfile

from twisted.application import service
from twisted.python import log, usage, filepath
from twisted.internet import reactor

from sparked import gui, stage, monitors, __version__


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
        if self.stage:
            if not self.baseOpts['debug']:
                self.stage.toggleFullscreen()
            stage.stageEvents.addObserver("stage-closed", lambda _: reactor.stop)


    def createStatusWindow(self):
        """
        Create the status window

        If your application does not need a status window, override
        this method in your application's subclass and return
        C{False}. This removes the dependency on the C{gtk} library.
        """
        gui.guiEvents.addObserver("statuswindow-closed", lambda _: reactor.stop)
        return gui.StatusWindow(self)


    def createStage(self):
        """
        Create the graphics stage.

        If your application does not need a graphics stage, override
        this method in your application's subclass and return
        C{False}. This removes the dependency on the C{clutter} library.
        """
        return stage.Stage(self)


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
                v = m.__version__
            else:
                v = ""
            print "%s %s (sparked %s)" % (self.appName, v, __version__)
        exit(0)



def getTempPath(modulename, id=None):
    if id:
        path = id
    else:
        path = modulename
    p = filepath.FilePath(tempfile.gettempdir()).child(path)
    if not p.exists():
        p.createDirectory()
    return p


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
