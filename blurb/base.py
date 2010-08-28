# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

import time

from twisted.application import service
from twisted.python import log
from twisted.internet import reactor

from blurb import events


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

    def __init__(self, baseOpts, pluginOpts):
        service.MultiService.__init__(self)

        self.baseOpts = baseOpts
        self.pluginOpts = pluginOpts

        self.state = StateMachine(self)
        reactor.callLater(0, self.state.set, "start")



class StateMachine (object):
    """
    A simple state machine.

    This machine is linked to a parent class, on which it calls
    enter_<state> and exit_<state> methods on state change. Also
    provided is a mechanism for timed state changes.
    """

    _state = None
    _statechanger = None


    def __init__(self, parent):
        self.parent = parent


    def set(self, newstate):
        """
        Sets a new state. Calls parent's state transition functions,
        if they exist.
        """

        if self._statechanger and self._statechanger.active():
            self._statechanger.cancel()

        if self._state:
            try:
                getattr(self.parent, 'exit_%s' % self._state)()
            except AttributeError:
                pass

        log.msg("%s --> %s" % (self._state, newstate))
        self._state = newstate

        try:
            getattr(self.parent, 'enter_%s' % self._state)()
        except AttributeError:
            pass


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



systemEvents = events.EventGroup()
