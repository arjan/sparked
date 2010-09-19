import clutter
import cluttergst
import gst

from sparked import application

from sparked.hardware import video
from sparked.graphics import stage



class Application(application.Application):
    title = "Video demo"

    def started(self):
        self.stage = Stage(self)

        m = VideoMonitor(self)
        m.setServiceParent(self)



class Stage(stage.Stage):

    def addDevice(self, dev):
        """
        Gets a L{video.V4LDevice}, wraps it in a gst videosink and puts it on the clutter stage.
        """
        tex = clutter.Texture()
        tex.show()
        self.add(tex)
        sink = cluttergst.VideoSink(tex)
        
        pipeline = gst.parse_launch(dev.getPipeline("video/x-raw-yuv", "320x240") + " ! queue name=t")
        pipeline.add(sink)
        gst.element_link_many(pipeline.get_by_name("t"), sink)
        pipeline.set_state(gst.STATE_PLAYING)

        #stage.positionInBox(tex, self)



class VideoMonitor(video.V4LDeviceMonitor):
    """
    Watches for cameras. If a camera connects, its live feed is started and put on the stage.
    """
    
    def __init__(self, app):
        video.V4LDeviceMonitor.__init__(self)
        self.app = app

    def deviceAdded(self, i):
        dev = video.V4LDevice(i['unique_path'], i['version'])
        print dev
        self.app.stage.addDevice(dev)


    def deviceRemoved(self, i):
        pass
