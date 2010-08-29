# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

from twisted.application.service import ServiceMaker

Spark = ServiceMaker(
        "Spark",
        "spark.tap",
        "Spark application launcher",
        "spark")
