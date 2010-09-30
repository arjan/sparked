from sparked.hardware.inputevent import InputEventDevice, InputEventProtocol, EV_KEY, EV_REL

class PowermateProtocol (InputEventProtocol):

    def eventReceived(self, e):
        if e.etype == EV_KEY:
            print "Button", e.evalue
        if e.etype == EV_REL:
            print "Move", e.evalue


from sparked import application

class Application(application.Application):

    title = "Griffin PowerMate example"

    def started(self):
        path = "/dev/input/by-id/usb-Griffin_Technology__Inc._Griffin_PowerMate-event-if00"
        self.powermate = InputEventDevice(PowermateProtocol(), path)
