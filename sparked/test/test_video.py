# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Tests for sparked.hardware.video

Maintainer: Arjan Scherpenisse
"""

import gst

from twisted.trial import unittest

from sparked.hardware import video

class TestVideoUtil(unittest.TestCase):
    """
    Test the L{sparked.graphics.video}
    """

    def testParseResolution(self):

        self.assertEqual( (640, 480), video.parseResolution("640x480"))
        self.assertEqual( (320, 480), video.parseResolution("320x480"))
        self.assertRaises( ValueError, video.parseResolution, "680x")
        self.assertRaises( ValueError, video.parseResolution, "680xBlah")
        self.assertRaises( ValueError, video.parseResolution, "blah")


class TestVideoDevices(unittest.TestCase):

    def setUp(self):
        self.dev = video.V4LVideoDevice("/dev/zero")
        self.dev._resolutions = []
        self.dev._resolutions.append( {"width": 320, "height": 240, "framerate": gst.Fraction(10,1)} )


    def testSelectBest(self):
        dev = video.V4LVideoDevice("/dev/zero")

        dev._resolutions = []
        dev._resolutions.append( {"mime": "image/jpeg"})
        self.assertEqual("image/jpeg", dev.getBestMime())

        dev._resolutions = []
        dev._resolutions.append( {"mime": "video/x-raw-rgb"})
        dev._resolutions.append( {"mime": "video/x-raw-yuv"})
        self.assertEqual("video/x-raw-yuv", dev.getBestMime())

        dev._resolutions = []
        dev._resolutions.append( {"width": 320, "height": 240})
        dev._resolutions.append( {"width": 321, "height": 241})
        self.assertEqual({"width": 321, "height": 241}, dev.getHighestResolution())
        self.assertEqual({"width": 321, "height": 241}, dev.getResolution("auto"))
        self.assertEqual({"width": 321, "height": 241}, dev.getResolution("highest"))

        dev._resolutions = []
        dev._resolutions.append( {"width": 320, "height": 240, "framerate": gst.Fraction(10,1)})
        dev._resolutions.append( {"width": 320, "height": 240, "framerate": gst.Fraction(15,1)})
        dev._resolutions.append( {"width": 320, "height": 240, "framerate": gst.Fraction(30,1)})
        self.assertEqual({"width": 320, "height": 240, "framerate": gst.Fraction(30,1)}, dev.getHighestResolution())

        dev._resolutions = []
        dev._resolutions.append( {"mime": "image/jpeg", "width": 320, "height": 240})
        dev._resolutions.append( {"mime": "video/x-raw-rgb", "width": 1000, "height": 1000})
        dev._resolutions.append( {"mime": "image/jpeg", "width": 321, "height": 241})
        self.assertEqual({"mime": "image/jpeg", "width": 321, "height": 241}, dev.getHighestResolution(mime="image/jpeg"))
        self.assertEqual({"mime": "image/jpeg", "width": 321, "height": 241}, dev.getResolution("auto", mime="image/jpeg"))
        self.assertEqual({"mime": "image/jpeg", "width": 321, "height": 241}, dev.getResolution("highest", mime="image/jpeg"))

        dev._resolutions = []
        dev._resolutions.append( {"mime": "image/jpeg", "framerate": gst.Fraction(10,1)})
        dev._resolutions.append( {"mime": "image/jpeg", "framerate": gst.Fraction(11,1)})
        self.assertEqual({"mime": "image/jpeg", "framerate": gst.Fraction(11,1)}, dev.getFastestResolution())
        self.assertEqual({"mime": "image/jpeg", "framerate": gst.Fraction(11,1)}, dev.getResolution("fastest"))


        dev._resolutions = []
        dev._resolutions.append( {"mime": "image/jpeg", "framerate": gst.Fraction(10,1), "width": 10, "height": 10})
        dev._resolutions.append( {"mime": "image/jpeg", "framerate": gst.Fraction(10,1), "width": 11, "height": 11})
        dev._resolutions.append( {"mime": "image/jpeg", "framerate": gst.Fraction(10,1), "width": 20, "height": 20})
        self.assertEqual({"mime": "image/jpeg", "framerate": gst.Fraction(10,1), "width": 20, "height": 20}, dev.getFastestResolution())


        dev._resolutions = []
        dev._resolutions.append( {"mime": "image/jpeg", "framerate": gst.Fraction(10,1)})
        dev._resolutions.append( {"mime": "video/blah", "framerate": gst.Fraction(30,1)})
        dev._resolutions.append( {"mime": "image/jpeg", "framerate": gst.Fraction(11,1)})
        self.assertEqual({"mime": "image/jpeg", "framerate": gst.Fraction(11,1)}, dev.getFastestResolution(mime="image/jpeg"))
        self.assertEqual({"mime": "image/jpeg", "framerate": gst.Fraction(11,1)}, dev.getResolution("fastest", mime="image/jpeg"))

        dev._resolutions = []
        self.assertEqual(None, dev.getResolution("320x240"))

        dev._resolutions = []
        self.assertEqual(None, dev.getResolution("320x240", "image/jpeg"))

        dev._resolutions = []
        dev._resolutions.append( {"width": 320, "height": 240, "mime": "video/x-raw-rgb"})
        dev._resolutions.append( {"width": 320, "height": 240, "mime": "video/x-raw-yuv"})
        dev._resolutions.append( {"width": 320, "height": 240, "mime": "video/x-raw-rgb"})
        self.assertEqual({"width": 320, "height": 240, "mime": "video/x-raw-yuv"}, dev.getResolution("320x240"))

        dev._resolutions = []
        dev._resolutions.append( {"width": 320, "height": 240, "mime": "image/jpeg"})
        dev._resolutions.append( {"width": 320, "height": 240, "mime": "video/x-raw-yuv"})
        dev._resolutions.append( {"width": 320, "height": 240, "mime": "video/x-raw-rgb"})
        self.assertEqual({"width": 320, "height": 240, "mime": "image/jpeg"}, dev.getResolution("320x240"))

        dev._resolutions = []
        dev._resolutions.append( {"width": 321, "height": 240, "mime": "image/jpeg"})
        dev._resolutions.append( {"width": 321, "height": 240, "mime": "video/x-raw-yuv"})
        dev._resolutions.append( {"width": 320, "height": 240, "mime": "video/x-raw-rgb"})
        self.assertEqual({"width": 320, "height": 240, "mime": "video/x-raw-rgb"}, dev.getResolution("320x240"))

        dev._resolutions = []
        dev._resolutions.append( {"width": 321, "height": 240, "mime": "image/jpeg"})
        dev._resolutions.append( {"width": 321, "height": 240, "mime": "video/x-raw-yuv"})
        dev._resolutions.append( {"width": 320, "height": 240, "mime": "video/x-raw-rgb"})
        self.assertEqual(None, dev.getResolution("320x240", "image/jpeg"))

        dev._resolutions = []
        dev._resolutions.append( {"width": 321, "height": 240, "mime": "video/x-raw-yuv"})
        dev._resolutions.append( {"width": 320, "height": 240, "mime": "video/x-raw-rgb"})
        dev._resolutions.append( {"width": 320, "height": 240, "mime": "image/jpeg"})
        self.assertEqual({"width": 320, "height": 240, "mime": "image/jpeg"}, dev.getResolution("320x240", "image/jpeg"))

        dev._resolutions = []
        dev._resolutions.append( {"width": 320, "height": 240, "mime": "image/jpeg", "framerate": gst.Fraction(30,1)})
        self.assertEqual("v4l2src device=/dev/zero ! image/jpeg,width=320,height=240,framerate=30/1", dev.getPipeline())
        self.assertEqual("v4l2src device=/dev/zero ! image/jpeg,width=320,height=240,framerate=30/1 ! jpegdec ! video/x-raw-rgb",
                         dev.getPipeline(outputMime="video/x-raw-rgb"))


        dev._resolutions = []
        dev._resolutions.append( {"width": 320, "height": 240, "mime": "image/jpeg", "framerate": gst.Fraction(30,1)})
        dev._resolutions.append( {"width": 640, "height": 480, "mime": "image/jpeg", "framerate": gst.Fraction(15,1)})
        self.assertEqual("v4l2src device=/dev/zero ! image/jpeg,width=320,height=240,framerate=30/1", dev.getPipeline())

        dev._resolutions = []
        dev._resolutions.append( {"width": 320, "height": 240, "mime": "image/jpeg", "framerate": gst.Fraction(30,1)})
        dev._resolutions.append( {"width": 640, "height": 480, "mime": "image/jpeg", "framerate": gst.Fraction(15,1)})
        self.assertEqual("v4l2src device=/dev/zero ! image/jpeg,width=320,height=240,framerate=30/1", dev.getPipeline())

        dev._resolutions = []
        dev._resolutions.append( {"width": 320, "height": 240, "mime": "image/jpeg", "framerate": gst.Fraction(30,1)})
        dev._resolutions.append( {"width": 640, "height": 480, "mime": "image/jpeg", "framerate": gst.Fraction(30,1)})
        self.assertEqual("v4l2src device=/dev/zero ! image/jpeg,width=640,height=480,framerate=30/1", dev.getPipeline())
