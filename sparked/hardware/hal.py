# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Hardware monitoring classes based on linux' HAL system.
"""

import dbus

from twisted.application import service
from twisted.internet import reactor


DBUS_INTERFACE = "org.freedesktop.DBus"
HAL_INTERFACE = 'org.freedesktop.Hal'
HAL_DEVICE_INTERFACE = 'org.freedesktop.Hal.Device'
HAL_MANAGER_INTERFACE = 'org.freedesktop.Hal.Manager'
HAL_MANAGER_UDI = '/org/freedesktop/Hal/Manager'



class HardwareMonitor (service.Service):
    """
    A generic hardware monitor class based on HAL. Listens for device add/remove filtered on a specific subsystem.
    """

    # e.g., 'serial', 'video4linux'
    subsystem = None

    # dict (by UDI) which will be filled with runtime info on device.
    deviceInfo = None


    def startService(self):
        self.deviceInfo = {}
        self.bus = dbus.SystemBus()
        self.bus.add_signal_receiver(self.deviceAdded,
                                dbus_interface=HAL_MANAGER_INTERFACE,
                                signal_name='DeviceAdded')
        self.bus.add_signal_receiver(self.deviceRemoved,
                                dbus_interface=HAL_MANAGER_INTERFACE,
                                signal_name='DeviceRemoved')

        self.manager = self.getHalInterface(HAL_MANAGER_UDI, HAL_MANAGER_INTERFACE)

        for udi in self.manager.FindDeviceByCapability(self.subsystem):
            reactor.callLater(0, self.deviceAdded, udi)


    def stopService(self):
        udis = self.deviceInfo.keys()
        for udi in udis:
            self.deviceRemoved(udi)


    def getHalInterface(self, udi, interface=HAL_DEVICE_INTERFACE):
        obj = self.bus.get_object(HAL_INTERFACE, udi)
        return dbus.Interface(obj, interface)


    def deviceAdded(self, udi):
        if not self.manager.DeviceExists(udi):
            # device has been removed
            return
        device = self.getHalInterface(udi)

        if not device.QueryCapability(self.subsystem):
            # wrong device
            return

        self.deviceInfo[udi] = {}
        return device


    def deviceRemoved(self, udi):
        if udi in self.deviceInfo:
            del self.deviceInfo[udi]
