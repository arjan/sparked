from twisted.internet import reactor
from sparked.hardware.inputevent import InputEventDevice, InputEventProtocol

d = InputEventDevice(InputEventProtocol(), "/dev/input/by-id/usb-Griffin_Technology__Inc._Griffin_PowerMate-event-if00", reactor)

reactor.run()
