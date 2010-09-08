# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Tests for sparked.graphics.*

Maintainer: Arjan Scherpenisse
"""

from twisted.trial import unittest

from sparked.graphics import util

class TestGraphicsUtil(unittest.TestCase):
    """
    Test the L{sparked.monitors.MonitorContainer}
    """

    def testParseColor(self):
        map = [
            ( (0,0,0), "000000"),
            ( (0,0,0), "000"),
            ( (0,0,0), "#000000"),
            ( (0,0,0), "#000"),
            ( (1,1,1), "FFFFFF"),
            ( (1,1,1), "FFF"),
            ( (1,1,1), "#FFFFFF"),
            ( (1,1,1), "#FFF")
            ]
            
        [self.assertEqual(a, util.parseColor(b)) for a,b in map]
