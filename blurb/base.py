# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

import time

from twisted.application import service
from twisted.python import log
from twisted.internet import reactor

from blurb import events, gui, stage


class Blurb(service.MultiService):
    """
    The blurb base class.

    All blurb plugins inherit from this class.

    @ivar state A L{StateMachine} instance which represents the main state of the Blurb application.
    @ivar baseOpts the basic options that are given on the blurb commandline; instance of L{blurb.launcher.Options}.
    @ivar pluginOpts the additional plugin commandline options; instance of L{yourplugin.Options}
    """

    state = None
    baseOpts = None
    pluginOpts = None


    statusWindow = None
    stage = None


    def __init__(self, baseOpts, pluginOpts):
        service.MultiService.__init__(self)

        self.baseOpts = baseOpts
        self.pluginOpts = pluginOpts

        self.state = StateMachine(self)

        reactor.callLater(0, self.startUp)
        reactor.callLater(0, self.state.set, "start")


    def startUp(self):
        """
        Create all services and GUI objects as needed.
        """
        self.statusWindow = self.createStatusWindow()
        if self.statusWindow:
            gui.guiEvents.addEventListener(lambda _: reactor.stop(), gui.StatusWindowClosed)

        self.stage = self.createStage()
        if self.stage:
            stage.stageEvents.addEventListener(lambda _: reactor.stop(), stage.StageClosed)


    def createStatusWindow(self):
        return gui.StatusWindow(self)


    def createStage(self):
        return stage.Stage(self)



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


systemEvents = events.EventGroup()
