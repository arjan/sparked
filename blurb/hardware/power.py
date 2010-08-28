# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Power monitor: fires events when AC power becomes (un)available; and
fires an event when the power becomes critically low.
"""

import dbus

from twisted.application import service
from blurb import events



class PowerAvailableEvent(events.Event):
    """
    Fired when the power state switches between running on battery and
    running on mains. The 'available' field contains a flag which is True
    when the computer is running on mains (AC) power.
    """



class LowPowerEvent(events.Event):
    """
    Fired when the battery state becomes critically low, or changes
    from critical back to normal. When the 'low' field of the event
    is True, the power is critically low.
    """
    pass



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
            bus.add_signal_receiver(self.power_event,
                                         dbus_interface=hal_interface,
                                         signal_name='OnBatteryChanged')
            bus.add_signal_receiver(self.lowpower_event,
                                         dbus_interface=hal_interface,
                                         signal_name='LowBatteryChanged')
            manager    = dbus.Interface(managerObj, hal_interface)

            self.power_event(manager.GetOnBattery())
            self.lowpower_event(manager.GetLowBattery())

        except dbus.exceptions.DBusException:
            # not found, try DeviceKit
            try:
                bus = dbus.SystemBus()
                dk_interface = 'org.freedesktop.DeviceKit.Power'
                dk_udi = '/org/freedesktop/DeviceKit/Power'

                managerObj = bus.get_object(dk_interface, dk_udi)
                bus.add_signal_receiver(self.dk_power_changed,
                                             dbus_interface=dk_interface,
                                             signal_name='Changed')
                manager    = dbus.Interface(managerObj, dk_interface)
                self.dk_properties = dbus.Interface(managerObj, 'org.freedesktop.DBus.Properties')
                self.dk_power_changed()

            except dbus.exceptions.DBusException:
                # finally, try UPower
                bus = dbus.SystemBus()
                dk_interface = 'org.freedesktop.UPower'
                dk_udi = '/org/freedesktop/UPower'

                managerObj = bus.get_object(dk_interface, dk_udi)
                bus.add_signal_receiver(self.up_power_changed,
                                             dbus_interface=dk_interface,
                                             signal_name='Changed')
                manager    = dbus.Interface(managerObj, dk_interface)
                self.up_properties = dbus.Interface(managerObj, 'org.freedesktop.DBus.Properties')
                self.up_power_changed()


    def up_power_changed(self):
        """
        Called when DeviceKit signals that something with the power has changed.
        """
        dk_interface = 'org.freedesktop.UPower'
        self.power_event(self.up_properties.Get(dk_interface, "OnBattery"))
        self.lowpower_event(self.up_properties.Get(dk_interface, "OnLowBattery"))


    def dk_power_changed(self):
        """
        Called when DeviceKit signals that something with the power has changed.
        """
        dk_interface = 'org.freedesktop.DeviceKit.Power'
        self.power_event(self.dk_properties.Get(dk_interface, "on-battery"))
        self.lowpower_event(self.dk_properties.Get(dk_interface, "on-low-battery"))


    def power_event(self, on_battery):
        """
        Called when the availability of the mains power changes.
        """
        powerEvents.sendEvent(PowerAvailableEvent(available = not on_battery))


    def lowpower_event(self, low):
        """
        Called when the 'lowpower' flag of the system changes.
        """
        powerEvents.sendEvent(LowPowerEvent(low=low))


powerEvents = events.EventGroup()
