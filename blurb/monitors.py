# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

from twisted.application import service

from blurb.hardware import power
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
        monitor.events.addEventListener(self.monitorEvent)


    def monitorEvent(self, e):
        print "!!!!", e



class Monitor(object):
    def __init__(self):
        self.events = events.EventGroup()

    def added(self, container):
        pass



class PowerMonitor (Monitor):
    def added(self, container):
        svc = power.PowerService()
        svc.setServiceParent(container)
        power.powerEvents.addEventListener(self.powerEvent)

    def powerEvent(self, e):
        self.events.sendEvent(e)


class NetworkMonitor(Monitor):
    pass

