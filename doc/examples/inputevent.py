# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
An example that reads raw input events from a Griffin Powermate
device.  You need to have write access on the corresponding
/dev/input/* device (and a powermate connected!) to run this example.

Example can easily be changed to reading mouse or keyboard events.
"""

from sparked import application
from sparked.hardware.inputevent import InputEventDevice, InputEventProtocol, EV_KEY, EV_REL

class PowermateProtocol (InputEventProtocol):

    def eventReceived(self, e):
        if e.etype == EV_KEY:
            print "Button", e.evalue
        if e.etype == EV_REL:
            print "Move", e.evalue



class Application(application.Application):

    title = "Griffin PowerMate example"

    def started(self):
        path = "/dev/input/by-id/usb-Griffin_Technology__Inc._Griffin_PowerMate-event-if00"
        self.powermate = InputEventDevice(PowermateProtocol(), path)
