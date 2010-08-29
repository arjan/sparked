# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Network monitoring class: check if the internet is reachable.
"""

import dbus

from twisted.application import service
from twisted.web import client
from twisted.internet import reactor, defer

from blurb import events


class NetworkConnectionEvent(events.Event):
    """
    Sent when NetworkManager connection changes.
    """


class NetworkWebConnectionEvent(events.Event):
    """
    Sent on every 'ping' of the web page request. 'connected' argument
    is True if it succeeded, or False if not.
    """


class NetworkConnectionService(service.Service):
    """
    Check on network connection existence through NetworkManager.
    """

    def startService(self):
        bus = dbus.SystemBus()
        interface = 'org.freedesktop.NetworkManager'
        udi = '/org/freedesktop/NetworkManager'

        managerObj = bus.get_object(interface, udi)
        bus.add_signal_receiver(self.stateChanged,
                                dbus_interface=interface,
                                signal_name='PropertiesChanged')
        self.properties = dbus.Interface(managerObj, 'org.freedesktop.DBus.Properties')
        self.stateChanged()


    def stateChanged(self, *a):
        interface = 'org.freedesktop.NetworkManager'
        state = self.properties.Get(interface, "ActiveConnections")
        self.connected = len(state) > 0
        networkEvents.sendEvent(NetworkConnectionEvent(connected=self.connected))



class NetworkWebConnectionService(service.Service):
    """
    Checks if the network connection is up by trying to reach a website.
    """

    url = "http://www.google.com/"
    delay = 30

    def startService(self):
        self.connected = False
        self.loop()
        # Listen to events from NetworkManager
        networkEvents.addEventListener(self.event, NetworkConnectionEvent)


    def loop(self):
        d = client.getPage(self.url)
        def ok(_):
            if not self.connected:
                networkEvents.sendEvent(NetworkWebConnectionEvent(connected=True))
            self.connected = True
        d.addCallback(ok)

        def error(f):
            print f
            if self.connected:
                networkEvents.sendEvent(NetworkWebConnectionEvent(connected=False))
            self.connected = False
        d.addErrback(error)

        d = defer.Deferred()
        self._dc = reactor.callLater(self.delay, lambda : d.callback(None))
        d.addCallback(lambda _: self.loop())
        return d


    def event(self, e):
        """
        Event from networkmanager came in. If network connection is
        down, do not try to fetch webpages.
        """
        if self._dc and self._dc.active():
            self._dc.cancel()

        self.connected = False
        if e.connected:
            self.loop()
        else:
            networkEvents.sendEvent(NetworkWebConnectionEvent(connected=False))


networkEvents = events.EventGroup()
