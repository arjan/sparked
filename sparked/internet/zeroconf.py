# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
A mixin object for Service instances that announce the service over Zeroconf.
"""

import avahi
import dbus

from twisted.python import log
from sparked import events


class _ZeroconfService (object):
    """
    A globally defined object which interfaces with avahi.
    """

    def __init__(self):
        self.published = {}
        self.server = None
        self.bus = None
        self.subscribed = []


    def publishService(self, name, stype, port, domain="", host=""):
        """
        Publish a named service on the local zeroconf network.
        """
        if name in self.published:
            return

        if not self.bus:
            self.bus = dbus.SystemBus()

        server = dbus.Interface(
                         self.bus.get_object(
                                 avahi.DBUS_NAME,
                                 avahi.DBUS_PATH_SERVER),
                        avahi.DBUS_INTERFACE_SERVER)

        g = dbus.Interface(
                    self.bus.get_object(avahi.DBUS_NAME,
                                   server.EntryGroupNew()),
                    avahi.DBUS_INTERFACE_ENTRY_GROUP)

        g.AddService(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC,dbus.UInt32(0),
                     name, stype, domain, host,
                     dbus.UInt16(port), "")

        g.Commit()
        self.published[name] = g


    def unpublishService(self, name):
        """
        Revoke a previously published service.
        """
        self.published[name].Reset()
        del self.published[name]


    def unpublishAllServices(self):
        """
        Revoke all published services.
        """
        for k in self.published.keys():
            self.unpublishService(k)



    def subscribeTo(self, serviceType):
        """
        Subscribe to a specific service.
        """
        if serviceType in self.subscribed:
            return

        if not self.bus:
            self.bus = dbus.SystemBus()
        if not self.server:
            self.server = dbus.Interface( self.bus.get_object(avahi.DBUS_NAME, '/'), 'org.freedesktop.Avahi.Server')

        sbrowser = dbus.Interface(self.bus.get_object(avahi.DBUS_NAME,
                                                      self.server.ServiceBrowserNew(avahi.IF_UNSPEC,
                                                                                    avahi.PROTO_UNSPEC, serviceType, 'local', dbus.UInt32(0))),
                                                                    avahi.DBUS_INTERFACE_SERVICE_BROWSER)
        sbrowser.connect_to_signal("ItemNew", self._itemNew)
        sbrowser.connect_to_signal("ItemRemove", self._itemRemove)
        self.subscribed.append(serviceType)


    # Avahi handler functions

    def _itemNew(self, iface, protocol, name, stype, domain, flags):

        def resolveError(*a):
            log.msg("RESOLVE ERROR:")
            log.err(a)

        def resolveSuccess(*args):
            name = args[2]
            hostname = args[5]
            address = args[7]
            port = args[8]
            log.msg("** New service: %s (%s@%s)" % (name, hostname, port))
            zeroconfEvents.dispatch("service-found", name, hostname=hostname, address=address, port=port, type=stype)

        self.server.ResolveService(iface, protocol, name, stype, 
                                   domain, avahi.PROTO_UNSPEC, dbus.UInt32(0), 
                                   reply_handler=resolveSuccess, error_handler=resolveError)



    def _itemRemove(self, iface, protocol, name, stype, domain, flags):
        log.msg("** Service lost: %s" % name)
        zeroconfEvents.dispatch("service-lost", name, type=stype)


try:
    zeroconfService
except NameError:
    zeroconfService = _ZeroconfService()
    zeroconfEvents = events.EventDispatcher()


__all__  = ['zeroconfService', 'zeroconfEvents']
