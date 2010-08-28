# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

from twisted.application.service import ServiceMaker

Blurb = ServiceMaker(
        "Blurb",
        "blurb.tap",
        "Blurb application launcher",
        "blurb")
