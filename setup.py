#!/usr/bin/env python
# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
spark installation script
"""

from setuptools import setup
import os
import sys
import subprocess
import spark
from twisted.python import procutils

setup(
    name = "spark",
    version = spark.__version__,
    author = "Arjan Scherpenisse",
    author_email = "arjan@scherpenisse.net",
    url = "http://bitbucket.org/arjan/spark",
    description = "Application development framework for interactive installations",
    scripts = [
        "bin/spark"
        ],
    license="MIT/X",
    packages = ['spark',
                'spark.hardware',
                'spark.test',
                'twisted.plugins'],
    package_data = {'twisted': ['plugins/spark.py']},

    long_description = """   """,
    classifiers = [
        "Framework :: Twisted",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Communications",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities"
        ]
    )

# if sys.argv[1] == "build":
#     commands = [
#         'help2man --no-info --include=man-osc-send.txt --no-discard-stderr --name="sends an OSC message" ./scripts/osc-send --output=osc-send.1',
#         'help2man --no-info --include=man-osc-receive.txt --no-discard-stderr --name="receives OSC messages" ./scripts/osc-receive --output=osc-receive.1',
#         ]
#     if os.path.exists("man-osc-send.txt"):
#         try:
#             help2man = procutils.which("help2man")[0]
#         except IndexError:
#             print("Cannot build the man pages. help2man was not found.")
#         else:
#             for c in commands:
#                 print("$ %s" % (c))
#                 retcode = subprocess.call(c, shell=True)
#                 print("The help2man command returned %s" % (retcode))

