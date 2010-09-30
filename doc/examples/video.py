# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
An example that launches a fullscreen stage and puts live video
streams on it for the webcams that you plug in. Hotpluggin is
supported: the webcams will start streaming as soon as the device is
detected.
"""

import clutter
import cluttergst
import gst

from sparked import application

from sparked.hardware import video
from sparked.graphics import stage

class Options(application.Options):
    optParameters = [
        ["resolution", "r", "640x480", "Camera resolution. Use 'auto' for best resolution."]
        ]

__version__ = "0.1.0"


class Application(application.Application):
    title = "Video demo"

    def started(self):
        self.stage = Stage(self)

        m = VideoMonitor(self)
        m.setServiceParent(self)


class Stage(stage.Stage):

    def addDevice(self, dev):
        """
        Gets a L{video.V4LDevice}, wraps it in a gst videosink and
        puts it on the clutter stage on a random position.
        """
        tex = clutter.Texture()
        tex.show()
        self.add(tex)
        sink = cluttergst.VideoSink(tex)

        pipeline = gst.parse_launch(dev.getPipeline("video/x-raw-yuv", self.app.appOpts["resolution"]) + " ! queue name=t")
        pipeline.add(sink)
        gst.element_link_many(pipeline.get_by_name("t"), sink)
        pipeline.set_state(gst.STATE_PLAYING)

        from random import random
        tex.set_position(random()*(self.get_width()-tex.get_width()), random()*(self.get_height()-tex.get_height()))



class VideoMonitor(video.V4LDeviceMonitor):
    """
    Watches for cameras. If a camera connects, its live feed is started and put on the stage.
    """

    def __init__(self, app):
        video.V4LDeviceMonitor.__init__(self)
        self.app = app

    def deviceAdded(self, i):
        dev = video.V4LDevice(i['unique_path'], i['version'])
        self.app.stage.addDevice(dev)

    def deviceRemoved(self, i):
        pass
