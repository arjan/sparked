
from twisted.internet import reactor

from sparked import application
from sparked.hardware import video



class Application(application.Application):

    def startService(self):
        application.Application.startService(self)
        v = video.V4LVideoDevice("/dev/video0")
        v.probe()
        print v.resolutions


    def createStage(self):
        return False


    def createStatusWindow(self):
        return False

