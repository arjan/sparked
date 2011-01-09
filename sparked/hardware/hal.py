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
    'input': ['device'],
    'usb': ['product', 'vendor', 'serial', 'vendor_id', 'product_id', 'interface.description']
    }


class HardwareMonitor (service.Service):
    """
    A generic hardware monitor class based on HAL. Listens for device add/remove filtered on a specific subsystem.

    @ivar subsystem: The HAL subsystem type to monitor. E.g. serial, video4linux, ...
    @ivar deviceInfo: dict which will be filled with device information. Key is the HAL UDI (Unique Device Identifier).
    @ivar uniquePath: If set, point to a directory where the symlinks to the unique devices will be made, e.g. /dev/serial/by-id/
    @ivar events: If set, point to a L{sparked.events.EventDispatcher} to dispatch <subsystem>-{added,removed} events to.
    """

    subsystem = None
    deviceInfo = None
    uniquePath = None
    events = None


    def startService(self):
        self.deviceInfo = {}
        self.bus = dbus.SystemBus()
        self.bus.add_signal_receiver(self._halDeviceAdded,
                                dbus_interface=HAL_MANAGER_INTERFACE,
                                signal_name='DeviceAdded')
        self.bus.add_signal_receiver(self._halDeviceRemoved,
                                dbus_interface=HAL_MANAGER_INTERFACE,
                                signal_name='DeviceRemoved')

        self.manager = self._getHalInterface(HAL_MANAGER_UDI, HAL_MANAGER_INTERFACE)

        for udi in self.manager.FindDeviceByCapability(self.subsystem):
            reactor.callLater(0, self._halDeviceAdded, udi)


    def stopService(self):
        udis = self.deviceInfo.keys()
        for udi in udis:
            self._halDeviceRemoved(udi)


    def _getHalInterface(self, udi, interface=HAL_DEVICE_INTERFACE):
        obj = self.bus.get_object(HAL_INTERFACE, udi)
        return dbus.Interface(obj, interface)


    def _halDeviceAdded(self, udi):
        udi = str(udi)
        if not self.manager.DeviceExists(udi):
            # device has been removed
            return
        device = self._getHalInterface(udi)

        if not device.QueryCapability(self.subsystem):
            # wrong device
            return

        self.deviceInfo[udi] = {"udi": udi}

        if self.subsystem in HAL_SUBSYSTEM_PROPERTIES:
            for k in HAL_SUBSYSTEM_PROPERTIES[self.subsystem]:
                self.deviceInfo[udi][k] = str(device.GetProperty(self.subsystem+'.'+k))

        # get the USB description
        if "originating_device" in self.deviceInfo[udi]:
            usbDevice = self._getHalInterface(self.deviceInfo[udi]["originating_device"])
            for k in HAL_SUBSYSTEM_PROPERTIES['usb']:
                self.deviceInfo[udi]['usb.' + k] = str(usbDevice.GetProperty('usb.'+k))

        print self.deviceInfo

        # get the device name
        if "device" in self.deviceInfo[udi] and self.uniquePath:
            by_id = [p for p in glob.glob(os.path.join(self.uniquePath, "*"))
                     if os.path.realpath(p) == self.deviceInfo[udi]["device"]]
            if by_id:
                self.deviceInfo[udi]["unique_path"] = by_id[0]

        if self.events:
            self.events.dispatch("%s-added" % self.subsystem, info=self.deviceInfo[udi])

        self.deviceAdded(self.deviceInfo[udi])
        return device


    def _halDeviceRemoved(self, udi):
        udi = str(udi)
        if udi not in self.deviceInfo:
            return

        if self.events:
            self.events.dispatch("%s-removed" % self.subsystem, info=self.deviceInfo[udi])

        self.deviceRemoved(self.deviceInfo[udi])
        del self.deviceInfo[udi]


    def deviceAdded(self, info):
        """
        This method will be called when a device has been added. If
        you subclass this class, this method can be overruled to do
        application-specific stuff.
        """


    def deviceRemoved(self, info):
        """
        This method will be called when a device has been removed. If
        you subclass this class, this method can be overruled to do
        application-specific stuff.
        """

