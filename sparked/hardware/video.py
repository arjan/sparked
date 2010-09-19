# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

import gst

from twisted.python import log

from sparked import events
from sparked.hardware import hal


class V4LDeviceMonitor (hal.HardwareMonitor):
    """
    Video device monitor.
    """
    subsystem = "video4linux"
    uniquePath = "/dev/v4l/by-id/"

    def __init__(self):
        self.events = videoEvents

videoEvents = events.EventDispatcher()
""" Event dispatcher for serial events """



class V4LDevice (object):
    """
    Represents a V4L video input device.
    """

    def __init__(self, device, v4l2version=2):
        self.preferMimes = ["image/jpeg", "video/x-raw-yuv", "video/x-raw-rgb"]
        self.setDevice(device, v4l2version)


    def _probe(self):
        """
        Find out the resolutions of the device
        """

        pipe = gst.parse_launch("%s name=source device=%s ! fakesink" % (self.gstSrc, self.device))
        pipe.set_state(gst.STATE_PAUSED)
        caps = pipe.get_by_name("source").get_pad("src").get_caps()

        self._resolutions = []

        for struct in caps:
            if struct.get_name() not in self.preferMimes:
                log.msg("mime \"%s\" currently not supported." % struct.get_name())
                continue
            if not isinstance(struct["width"], int):
                log.msg("\"range\" resolutions currently not supported.")
                continue
            if type(struct["framerate"]) == list:
                fr = min(struct["framerate"])
            else:
                fr = struct["framerate"]
            r = {'mime': struct.get_name(),
                 'width': struct['width'],
                 'height': struct['height'],
                 'framerate': fr}
            self.resolutions.append(r)
            pipe.set_state(gst.STATE_NULL)


    @property
    def resolutions(self):
        if self._resolutions is None:
            self._probe()
        return self._resolutions


    def setDevice(self, device, v4l2version=2):
        """
        Set the device
        """
        self.device = device

        self.v4l2version = v4l2version
        if str(self.v4l2version) == '2':
            self.gstSrc = "v4l2src"
        else:
            self.gstSrc = "v4lsrc"
        self._resolutions = None


    def getHighestResolution(self, mime=None):
        """
        Optionally given a mime, get the highest possible resolution, without
        taking framerate into account. Returns a resolution dict.
        """
        mxres = 0
        mx = None
        pref = self.preferMimes
        for r in self.resolutions:
            if mime and r['mime'] != mime:
                continue
            if not mx or r['width']*r['height']>mxres:
                mx = r
                mxres = r['width']*r['height']
            elif r['width']*r['height']==mxres and float(r['framerate'])>float(mx['framerate']):
                mx = r
            elif r['width']*r['height']==mxres and float(r['framerate'])==float(mx['framerate']) and pref.index(r['mime'])<pref.index(mx['mime']):
                mx = r
        return mx


    def getFastestResolution(self, mime=None):
        """
        Optionally given a mime, get the fastest possible resolution, without
        taking resolution into account. Returns a resolution dict.
        """
        mxfr = None
        mx = None
        pref = self.preferMimes
        for r in self.resolutions:
            if mime and r['mime'] != mime:
                continue
            if not mx or float(r['framerate'])>float(mxfr):
                mx = r
                mxfr = r['framerate']
            elif float(r['framerate'])==float(mxfr) and r['width']*r['height']>mx['width']*mx['height']:
                mx = r
            elif float(r['framerate'])==float(mxfr) and r['width']*r['height']==mx['width']*mx['height'] and pref.index(r['mime'])<pref.index(mx['mime']):
                mx = r

        return mx


    def getBestMime(self):
        """
        Return the best supported video mime type.
        """
        mime = None
        pref = self.preferMimes
        for r in self.resolutions:
            if not mime or pref.index(mime) > pref.index(r['mime']):
                mime = r['mime']
        return mime


    def getResolution(self, resolution, mime=None):
        if resolution == "auto" or resolution == "highest":
            return self.getHighestResolution(mime)
        if resolution == "fastest":
            return self.getFastestResolution(mime)

        w,h = parseResolution(resolution)
        mx = None
        pref = self.preferMimes
        for r in self.resolutions:
            if r['width'] != w or r['height'] != h:
                continue
            if mime and r['mime'] != mime:
                continue
            if not mx:
                mx = r
            elif pref.index(mx['mime']) > pref.index(r['mime']):
                mx = r
        return mx


    def getPipeline(self, outputMime=None, resolution="auto"):
        """
        Construct a string which is parsable as the "input" part of the pipeline for a gstreamer camera.
        """

        r = self.getResolution(resolution)
        if r is None:
            raise ValueError("Unsupported resolution: "+resolution)
        w, h = r['width'], r['height']
        inputMime = r['mime']
        framerate = r['framerate']

        if outputMime is None:
            outputMime = inputMime

        pipe = "%s device=%s ! %s,width=%d,height=%d,framerate=%d/%d" % (self.gstSrc, self.device, inputMime, w, h, framerate.num, framerate.denom)

        if inputMime == outputMime:
            return pipe
        if inputMime == "image/jpeg":
            pipe += " ! jpegdec"
        else:
            pipe += " ! ffmpegcolorspace"
        pipe += " ! " + outputMime
        return pipe


def parseResolution(res):
    try:
        return tuple(map(int, res.split("x")))
    except:
        raise ValueError("Invalid resolution: " + res)


