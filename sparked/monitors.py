# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.
# -*- test-case-name: sparked.test.test_monitors -*-

"""
Classes for monitoring the system's state.
"""

from twisted.application import service
from twisted.internet import reactor
from twisted.python import log

from sparked.hardware import power, network
from sparked.internet import zeroconf
from sparked import events



class MonitorContainer (service.MultiService):
    """
    A container for monitoring services.

    @ivar monitors: A list of L{Monitor} objects.
    @ivar events: An L{events.EventDispatcher} which triggers an "updated" event when one of the monitors state changes.
    """

    monitors = None
    events = None
    verbose = True

    lastState = None

    def __init__(self):
        service.MultiService.__init__(self)
        self.events = events.EventDispatcher()
        self.monitors = []


    def startService(self):
        service.MultiService.startService(self)
        reactor.callLater(0, self.update)


    def addMonitor(self, monitor):
        """
        Add a monitor to the container, and notify that the monitor
        has changed. A monitor can only be part of one container.
        """
        if monitor.container is not None:
            monitor.container.removeMonitor(monitor)
        monitor.container = self
        self.monitors.append(monitor)
        monitor.added()
        self.update()


    def removeMonitor(self, monitor):
        """
        Remove a monitor from the container. Raises ValueError if the
        monitor is not part of the container.
        """
        i = self.monitors.index(monitor)
        self.monitors[i].removed()
        self.monitors[i].container = None
        del self.monitors[i]
        self.update()


    def update(self):
        """
        Notify the container that monitor state has been changed or
        the monitors have been modified.
        """
        if self.state == self.lastState:
            return
        self.events.dispatch("updated", self)
        self.lastState = self.state
        if not self.verbose:
            return
        log.msg("= STATUS =====================")
        for m in self.monitors:
            stat = {None: "n/a", True: "ok", False: "FAIL"}[m.ok]
            log.msg("%-26s%4s" % (m.title, stat))
        log.msg("==============================")


    @property
    def ok(self):
        for m in self.monitors:
            if m.ok == False: return False
        return True


    @property
    def state(self):
        return tuple([m.ok for m in self.monitors])



class Monitor(object):
    """
    A generic monitor

    @ivar ok:  Boolean flag which tells if the monitor's state is 'ok' or not.
    """

    ok = None
    container = None
    title = "(monitor)"

    def added(self):
        """
        Called when monitor is added to a container. The container can
        be used to hook services to.
        """
        pass

    def removed(self):
        """
        Called when monitor is removed from container. The container can
        be used to hook services to.
        """
        pass



class PowerMonitor (Monitor):
    title = "Computer power"

    def added(self):
        self.svc = power.PowerService()
        self.svc.setServiceParent(self.container)
        power.powerEvents.addObserver("available", self.powerEvent)


    def removed(self):
        self.svc.disownServiceParent()


    def powerEvent(self, available):
        if available != self.ok:
            self.ok = available
            self.container.update()



class NetworkMonitor(Monitor):
    title = "Network connection"

    def added(self):
        self.svc = network.NetworkConnectionService()
        self.svc.setServiceParent(self.container)
        network.networkEvents.addObserver("connected", self.event)


    def removed(self):
        self.svc.disownServiceParent()


    def event(self, connected):
        if connected != self.ok:
            self.ok = connected
            self.container.update()



class NetworkWebMonitor(Monitor):
    title = "Internet connection"
    url = None

    def __init__(self, url="http://www.google.com/"):
        self.url = url


    def added(self):
        self.svc = network.NetworkWebConnectionService(self.url)
        self.svc.setServiceParent(self.container)
        network.networkEvents.addObserver("web-connected", self.event)


    def removed(self):
        self.svc.disownServiceParent()


    def event(self, connected):
        if connected != self.ok:
            self.ok = connected
            self.container.update()



class NamedZeroconfMonitor(Monitor):
    """
    Monitor which is 'ok' when it has detected a service with given
    type and name.

    @ivar type: The service type that needs to be matched. E.g. C{_daap._tcp}.
    @ivar name: The service name that needs to be matched. E.g. C{Arjan's Music}.
    """

    def __init__(self, name, type):
        self.name = name
        self.title = name
        self.type = type


    def added(self):
        zeroconf.zeroconfService.subscribeTo(self.type)
        zeroconf.zeroconfEvents.addObserver("service-found", self._found)
        zeroconf.zeroconfEvents.addObserver("service-lost", self._lost)


    def _found(self, name, **kw):
        if kw['type'] == self.type and name == self.name:
            self.ok = True
            self.container.update()


    def _lost(self, name, **kw):
        if kw['type'] == self.type and name == self.name:
            self.ok = False
            self.container.update()

