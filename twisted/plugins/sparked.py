# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

from twisted.application.service import ServiceMaker

Spark = ServiceMaker(
        "Sparked",
        "sparked.tap",
        "Sparked application launcher",
        "sparked")
