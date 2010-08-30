# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Power monitor: fires events when AC power becomes (un)available; and
fires an event when the power becomes critically low.
"""

import dbus

from twisted.application import service
from sparked import events


class PowerService(service.Service):
    """
    A service which monitors the power state of the computer. It fires
    L{PowerAvailableEvent}s and L{LowPowerEvent}s. On the startup of
    the service, these signals get fired once to ensure a valid system
    state.
    """

    def __init__(self):
        self.manager = None


    def startService(self):

        try:
            bus = dbus.Bus()
            hal_interface = 'org.freedesktop.PowerManagement'
            hal_udi = '/org/freedesktop/PowerManagement'

            managerObj = bus.get_object(hal_interface, hal_udi)
            bus.add_signal_receiver(self.powerEvent,
                                         dbus_interface=hal_interface,
                                         signal_name='OnBatteryChanged')
            bus.add_signal_receiver(self.lowpowerEvent,
                                         dbus_interface=hal_interface,
                                         signal_name='LowBatteryChanged')
            manager    = dbus.Interface(managerObj, hal_interface)

            self.powerEvent(manager.GetOnBattery())
            self.lowpowerEvent(manager.GetLowBattery())

        except dbus.exceptions.DBusException:
            # not found, try DeviceKit
            try:
                bus = dbus.SystemBus()
                dk_interface = 'org.freedesktop.DeviceKit.Power'
                dk_udi = '/org/freedesktop/DeviceKit/Power'

                managerObj = bus.get_object(dk_interface, dk_udi)
                bus.add_signal_receiver(self.dkPowerChanged,
                                             dbus_interface=dk_interface,
                                             signal_name='Changed')
                manager    = dbus.Interface(managerObj, dk_interface)
                self.dk_properties = dbus.Interface(managerObj, 'org.freedesktop.DBus.Properties')
                self.dkPowerChanged()

            except dbus.exceptions.DBusException:
                # finally, try UPower
                bus = dbus.SystemBus()
                dk_interface = 'org.freedesktop.UPower'
                dk_udi = '/org/freedesktop/UPower'

                managerObj = bus.get_object(dk_interface, dk_udi)
                bus.add_signal_receiver(self.upPowerChanged,
                                             dbus_interface=dk_interface,
                                             signal_name='Changed')
                manager    = dbus.Interface(managerObj, dk_interface)
                self.up_properties = dbus.Interface(managerObj, 'org.freedesktop.DBus.Properties')
                self.upPowerChanged()


    def upPowerChanged(self):
        """
        Called when UPower signals that something with the power has changed.
        """
        dk_interface = 'org.freedesktop.UPower'
        self.powerEvent(self.up_properties.Get(dk_interface, "OnBattery"))
        self.lowpowerEvent(self.up_properties.Get(dk_interface, "OnLowBattery"))


    def dkPowerChanged(self):
        """
        Called when DeviceKit signals that something with the power has changed.
        """
        dk_interface = 'org.freedesktop.DeviceKit.Power'
        self.powerEvent(self.dk_properties.Get(dk_interface, "on-battery"))
        self.lowpowerEvent(self.dk_properties.Get(dk_interface, "on-low-battery"))


    def powerEvent(self, onBattery):
        """
        Called when the power state switches between running on battery and
        running on mains. The 'available' field contains a flag which is True
        when the computer is running on mains (AC) power.
        """
        powerEvents.dispatch("available", not onBattery)


    def lowpowerEvent(self, low):
        """
        Called when the battery state becomes critically low, or
        changes from critical back to normal. When the 'low' field of
        the event is True, the power is critically low.  Triggers a
        'low' event on this module's dispatcher.
        """
        powerEvents.dispatch("low", low)


powerEvents = events.EventDispatcher()
