import gst

from sparked import application
from sparked.hardware import video



class Application(application.Application):

    def startService(self):
        application.Application.startService(self)
        v = video.V4LDevice("/dev/video0")
        pipe = "%s ! autovideosink" % v.getPipeline(outputMime="video/x-raw-yuv")
        print pipe
        p = gst.parse_launch(pipe)
        print p
        p.set_state(gst.STATE_PLAYING)

    def createStage(self):
        return False


    def createStatusWindow(self):
        return False

