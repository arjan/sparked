# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

from twisted.application import service

from blurb.hardware import power, network
from blurb import events



class MonitorEvent(events.Event):
    pass



class MonitorContainer (service.MultiService):
    """
    A container for monitoring services.
    """

    monitors = None

    def __init__(self):
        service.MultiService.__init__(self)
        self.monitors = []


    def addMonitor(self, monitor):
        self.monitors.append(monitor)
        monitor.added(self)


    def ping(self):
        """
        Notify the container that monitor state has been changed.
        """

        print [(m.title, m.ok) for m in self.monitors]


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


