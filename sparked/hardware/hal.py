# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Hardware monitoring classes based on linux' HAL system.
"""

import os
import dbus
import glob

from twisted.application import service
from twisted.internet import reactor


DBUS_INTERFACE = "org.freedesktop.DBus"
HAL_INTERFACE = 'org.freedesktop.Hal'
HAL_DEVICE_INTERFACE = 'org.freedesktop.Hal.Device'
HAL_MANAGER_INTERFACE = 'org.freedesktop.Hal.Manager'
HAL_MANAGER_UDI = '/org/freedesktop/Hal/Manager'

# The following properties get automatically read upon device insertion.
# See http://people.freedesktop.org/~dkukawka/hal-spec-git/hal-spec.html
#
HAL_SUBSYSTEM_PROPERTIES = {
    'serial': ['originating_device', 'device', 'port', 'type'],
    'video4linux': ['device', 'version'],
    'input': ['device']
    }


class HardwareMonitor (service.Service):
    """
    A generic hardware monitor class based on HAL. Listens for device add/remove filtered on a specific subsystem.

    @ivar subsystem: The HAL subsystem type to monitor. E.g. serial, video4linux, ...
    @ivar deviceInfo: dict which will be filled with device information. Key is the HAL UDI (Unique Device Identifier).
    @ivar uniquePath: If set, point to a directory where the symlinks to the unique devices will be made, e.g. /dev/serial/by-id/
    """

    subsystem = None
    deviceInfo = None
    uniquePath = None


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

        if self.subsystem in HAL_SUBSYSTEM_PROPERTIES:
            for k in HAL_SUBSYSTEM_PROPERTIES[self.subsystem]:
                self.deviceInfo[udi][k] = str(device.GetProperty(self.subsystem+'.'+k))

        if "device" in self.deviceInfo[udi] and self.uniquePath:
            by_id = [p for p in glob.glob(os.path.join(self.uniquePath, "*"))
                     if os.path.realpath(p) == self.deviceInfo[udi]["device"]]
            if by_id:
                self.deviceInfo[udi]["unique_path"] = by_id[0]

        return device


    def deviceRemoved(self, udi):
        if udi in self.deviceInfo:
            del self.deviceInfo[udi]
