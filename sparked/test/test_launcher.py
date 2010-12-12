# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Tests for sparked.launcher.*

Maintainer: Arjan Scherpenisse
"""
from twisted.python import usage, filepath
from twisted.trial import unittest

from sparked import launcher

class TestLauncher(unittest.TestCase):
    """
    Test the L{sparked.launcher}
    """

    def testLaunchMissingApplicationName(self):
        self.assertRaises(usage.UsageError, launcher.launchApplication, [])

    def testLaunchApplicationNotFound(self):
        self.assertRaises(usage.UsageError, launcher.launchApplication, ["somethingthatdoesnotexist"])


    def testSplitOptions(self):
        self.assertEquals( ([], None, []), launcher.splitOptions([]))
        self.assertEquals( (["-f"], None, []), launcher.splitOptions(["-f"]))
        self.assertEquals( ([], "bla", ["-f"]), launcher.splitOptions(["bla", "-f"]))
        self.assertEquals( (["-a"], "bla", ["-f"]), launcher.splitOptions(["-a", "bla", "-f"]))
        self.assertEquals( (["-a", "--b=bleh"], "bla", ["-f"]), launcher.splitOptions(["-a", "--b=bleh", "bla", "-f"]))


class TestQuitFlag(unittest.TestCase):

    def setUp(self):
        import tempfile
        self.flag = launcher.QuitFlag(filepath.FilePath(tempfile.mkstemp()[1]))

    def tearDown(self):
        self.flag.reset()

    def testSimple(self):
        self.assertEquals(False, self.flag.isSet())

    def testSet(self):
        self.flag.set()
        self.assertEquals(True, self.flag.isSet())

    def testSetReset(self):
        self.flag.set()
        self.assertEquals(True, self.flag.isSet())
        self.flag.reset()
        self.assertEquals(False, self.flag.isSet())
