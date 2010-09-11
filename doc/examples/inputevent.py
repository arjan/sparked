from twisted.internet import reactor
from sparked.hardware.inputevent import InputEventDevice, InputEventProtocol, EV_KEY, EV_REL

class PowermateProtocol (InputEventProtocol):

    def eventReceived(self, e):
        if e.etype == EV_KEY:
            print "Button", e.evalue
        if e.etype == EV_REL:
            print "Move", e.evalue

d = InputEventDevice(PowermateProtocol(), "/dev/input/by-id/usb-Griffin_Technology__Inc._Griffin_PowerMate-event-if00", reactor)

reactor.run()
