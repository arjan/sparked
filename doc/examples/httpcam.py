import gst
import os
import tempfile

from twisted.internet import reactor
from twisted.web.server import Site
from twisted.application import strports
from twisted.web import resource, static

from sparked import application
from sparked.hardware import video


class Options(application.Options):
    optParameters = [
        ["resolution", "r", "auto", "Camera resolution (e.g. 640x480)"],
        ["port", "p", "8080", "HTTP port"]
        ]



class Application(application.Application):
    title = "Pluggable HTTP cameras"

    def started(self):
        self.webserver = WebServer(self)

        httpService = strports.service(self.appOpts["port"], Site(self.webserver))
        httpService.setServiceParent(self)

        m = VideoMonitor(self)
        m.setServiceParent(self)



class WebServer(resource.Resource):

    def __init__(self, app):
        resource.Resource.__init__(self)
        self.app = app


    def render_GET(self, request):
        return "<html><body><h1>IkCam Slave</h1></body></html>"


    def addDevice(self, info, dev):
        """
        A camera was added to the system. 
        """
        pipeline = gst.parse_launch(dev.getPipeline("video/x-raw-rgb", self.app.appOpts["resolution"]) + " ! gdkpixbufsink name=sink send-messages=0")
        pipeline.set_state(gst.STATE_PLAYING)

        base = os.path.basename(info['device'])
        self.putChild(base, WebcamChild(pipeline))


    def removeDevice(self, info):
        base = os.path.basename(info['device'])
        del self.children[base]



class WebcamChild(resource.Resource):

    def __init__(self, pipeline):
        self.pipeline = pipeline


    def render_GET(self, request):
        sink = self.pipeline.get_by_name("sink")
        print sink
        print sink.get_property("last-pixbuf")
        pixbuf = sink.get_property("last-pixbuf")
        print pixbuf
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
        dev = video.V4LDevice(i['unique_path'], i['version'])
        print dev
        self.app.webserver.addDevice(i, dev)


    def deviceRemoved(self, i):
        self.app.webserver.removeDevice(i)

