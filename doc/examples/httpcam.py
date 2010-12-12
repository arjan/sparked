# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
A HTTP interface to your webcams. Exposes your all your webcams at
http://ip:2222/video{0,1,2..}. The interface is plug-n-play; all
webcams are detected and added to the webserver automatically.
http://ip:2222/ gives a self-refreshing overview of all webcam images.
"""

import gst
import os
import tempfile

from twisted.internet import reactor
from twisted.web.server import Site
from twisted.application import strports
from twisted.web import resource, static
from twisted.python import log

from sparked import application
from sparked.hardware import video


class Options(application.Options):
    optParameters = [
        ["resolution", "r", "auto", "Camera resolution (e.g. 640x480)"],
        ["port", "p", "2222", "HTTP port"]
        ]


class Application(application.Application):
    title = "Pluggable HTTP cameras"

    def started(self):
        # Create webserver
        self.webserver = WebServer(self)
        httpService = strports.service("tcp:"+self.appOpts["port"], Site(self.webserver))
        httpService.setServiceParent(self)

        # Create webcam monitor
        m = VideoMonitor(self)
        m.setServiceParent(self)



class WebServer(resource.Resource):

    def __init__(self, app):
        resource.Resource.__init__(self)
        self.app = app
        self.putChild("", self)


    def render_GET(self, request):
        """
        Render the overview page.
        """
        im = ["<img src=\"/%s\" />" % k for k in self.children.keys() if k != ""]
        return "<html><meta http-equiv=\"refresh\" content=\"1\" /><body><h1>HTTPcam</h1>%s</body></html>" % ("".join(im))


    def addDevice(self, info, dev):
        """
        A camera was added to the system. Launch a pipeline and add it as child.
        """
        try:
            pipeline = gst.parse_launch(dev.getPipeline("video/x-raw-yuv", self.app.appOpts["resolution"]) + " ! ffmpegcolorspace ! queue ! gdkpixbufsink name=sink send-messages=0")
            #pipeline = gst.parse_launch("videotestsrc ! tee ! queue ! gdkpixbufsink name=sink send-messages=1")
            base = os.path.basename(info['device'])
            self.putChild(base, WebcamChild(pipeline))
        except ValueError, e:
            log.err(e)
            reactor.stop()



    def removeDevice(self, info):
        """
        Camera was removed.
        """
        base = os.path.basename(info['device'])
        del self.children[base]



class WebcamChild(resource.Resource):
    """
    Grab an image from the webcam, save it temporarily and serve it as image/jpeg.
    """
    def __init__(self, pipeline):
        self.pipeline = pipeline
        pipeline.set_state(gst.STATE_PLAYING)

    def render_GET(self, request):
        sink = self.pipeline.get_by_name("sink")
        pixbuf = sink.get_property("last-pixbuf")
        fd, fn = tempfile.mkstemp(".jpg")
        os.close(fd)
        pixbuf.save(fn, "jpeg")
        f = static.File(fn, "image/jpeg")
        reactor.callLater(0, os.unlink, fn)
        return f.render(request)



class VideoMonitor(video.V4LDeviceMonitor):
    """
    Watches for cameras. If a camera connects, its live feed is started and put on the stage.
    """

    def __init__(self, app):
        video.V4LDeviceMonitor.__init__(self)
        self.app = app

    def deviceAdded(self, i):
        if 'unique_path' not in i: return
        dev = video.V4LDevice(i['unique_path'], i['version'])
        self.app.webserver.addDevice(i, dev)

    def deviceRemoved(self, i):
        self.app.webserver.removeDevice(i)


if __name__ == "__main__":
    from sparked import launcher
    launcher.launchHelp(__file__)
