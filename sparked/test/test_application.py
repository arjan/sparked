# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Tests for sparked.application.*

Maintainer: Arjan Scherpenisse
"""

from twisted.trial import unittest

from sparked.application import getPath

class TestGetPath(unittest.TestCase):
    """
    Test the L{application.getPath}
    """

    def testTempPaths(self):
        self.assertEqual("/tmp/foo", getPath("temp", "foo", None).path)
        self.assertEqual("/tmp/bar", getPath("temp", "foo", "bar").path)
        self.assertEqual("/some/prefix/tmp", getPath("temp", "foo", None, "/some/prefix").path)


    def testLogPaths(self):
        self.assertEqual("/var/log/foo.log", getPath("log", "foo", None).path)
        self.assertEqual("/var/log/bar.log", getPath("log", "foo", "bar").path)
        self.assertEqual("/some/prefix/foo.log", getPath("log", "foo", None, "/some/prefix/").path)
        self.assertEqual("/some/prefix/bar.log", getPath("log", "foo", "bar", "/some/prefix/").path)


    def testPidPaths(self):
        self.assertEqual("/var/run/foo.pid", getPath("pid", "foo", None).path)
        self.assertEqual("/var/run/bar.pid", getPath("pid", "foo", "bar").path)
        self.assertEqual("/some/prefix/foo.pid", getPath("pid", "foo", None, "/some/prefix/").path)


    def testSharePaths(self):
        self.assertEqual("/usr/share/foo", getPath("share", "foo", None).path)
        self.assertEqual("/usr/share/foo", getPath("share", "foo", "bar").path)
        self.assertEqual("/some/prefix/share", getPath("share", "foo", None, "/some/prefix/").path)


    def testDataPaths(self):
        self.assertEqual("/var/lib/foo", getPath("data", "foo", None).path)
        self.assertEqual("/var/lib/bar", getPath("data", "foo", "bar").path)


    def testInvalidPath(self):
        self.assertRaises(ValueError, getPath, "xxxtemp", "foo", None)
