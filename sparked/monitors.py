# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.
# -*- test-case-name: sparked.test.test_monitors -*-

"""
Classes for monitoring the system's state.
"""

from twisted.application import service

from sparked.hardware import power, network
from sparked import events



class MonitorEvent(events.Event):
    pass



class MonitorContainer (service.MultiService):
    """
    A container for monitoring services.

    @ivar monitors: A list of L{Monitor} objects.
    @ivar events: An L{events.EventGroup} which triggers a L{MonitorEvent} when one of the monitors state changes.
    """

    monitors = None
    events = None

    def __init__(self):
        service.MultiService.__init__(self)
        self.events = events.EventGroup()
        self.monitors = []


    def addMonitor(self, monitor):
        """
        Add a monitor to the container, and notify that the monitor has changed.
        """
        self.monitors.append(monitor)
        monitor.added(self)
        self.ping()


    def ping(self):
        """
        Notify the container that monitor state has been changed or the monitors have been modified.
        """
        self.events.sendEvent(MonitorEvent(container=self))



class Monitor(object):
    """
    A generic monitor

    @ivar ok:  Boolean flag which tells if the monitor's state is 'ok' or not.
    """

    ok = False

    def added(self, container):
        """
        Called when monitor is added to container. The container can
        be used to hook services to.
        """
        pass



class PowerMonitor (Monitor):
    title = "Computer power"

    def added(self, container):
        self.container = container
        svc = power.PowerService()
        svc.setServiceParent(container)
        power.powerEvents.addEventListener(self.powerEvent, power.PowerAvailableEvent)


    def powerEvent(self, e):
        if e.available != self.ok:
            self.ok = e.available
            self.container.ping()



class NetworkMonitor(Monitor):
    title = "Network connection"

    def added(self, container):
        self.container = container
        svc = network.NetworkConnectionService()
        svc.setServiceParent(container)
        network.networkEvents.addEventListener(self.event, network.NetworkConnectionEvent)


    def event(self, e):
        if e.connected != self.ok:
            self.ok = e.connected
            self.container.ping()



class NetworkWebMonitor(Monitor):
    title = "Internet connection"

    def added(self, container):
        self.container = container
        svc = network.NetworkWebConnectionService()
        svc.setServiceParent(container)
        network.networkEvents.addEventListener(self.event, network.NetworkWebConnectionEvent)


    def event(self, e):
        if e.connected != self.ok:
            self.ok = e.connected
            self.container.ping()


