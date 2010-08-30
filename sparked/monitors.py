# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.
# -*- test-case-name: sparked.test.test_monitors -*-

"""
Classes for monitoring the system's state.
"""

from twisted.application import service
from twisted.internet import reactor

from sparked.hardware import power, network
from sparked import events



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
        self.events = events.EventDispatcher()
        self.monitors = []


    def startService(self):
        service.MultiService.startService(self)
        reactor.callLater(0, self.update)


    def addMonitor(self, monitor):
        """
        Add a monitor to the container, and notify that the monitor has changed.
        """
        self.monitors.append(monitor)
        monitor.added(self)
        self.update()


    def removeMonitor(self, monitor):
        """
        Remove a monitor from the container
        """
        i = self.monitors.index(monitor)
        self.monitors[i].removed(self)
        del self.monitors[i]
        self.update()


    def update(self):
        """
        Notify the container that monitor state has been changed or the monitors have been modified.
        """
        self.events.dispatch("updated", self)



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

    def removed(self, container):
        """
        Called when monitor is removed from container. The container can
        be used to hook services to.
        """
        pass



class PowerMonitor (Monitor):
    title = "Computer power"

    def added(self, container):
        self.container = container
        self.svc = power.PowerService()
        self.svc.setServiceParent(container)
        power.powerEvents.addObserver("available", self.powerEvent)


    def removed(self):
        self.svc.disownServiceParent()


    def powerEvent(self, available):
        if available != self.ok:
            self.ok = available
            self.container.update()



class NetworkMonitor(Monitor):
    title = "Network connection"

    def added(self, container):
        self.container = container
        self.svc = network.NetworkConnectionService()
        self.svc.setServiceParent(container)
        network.networkEvents.addObserver("connected", self.event)


    def removed(self):
        self.svc.disownServiceParent()


    def event(self, connected):
        if connected != self.ok:
            self.ok = connected
            self.container.update()



class NetworkWebMonitor(Monitor):
    title = "Internet connection"

    def added(self, container):
        self.container = container
        self.svc = network.NetworkWebConnectionService()
        self.svc.setServiceParent(container)
        network.networkEvents.addObserver("web-connected", self.event)


    def removed(self):
        self.svc.disownServiceParent()


    def event(self, connected):
        if connected != self.ok:
            self.ok = connected
            self.container.update()


