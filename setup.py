#!/usr/bin/env python
# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Sparked installation script
"""

from setuptools import setup
import os
import sys
import subprocess
import sparked
from twisted.python import procutils


if sys.argv[1] == "build":
    commands = [
        'PYTHONPATH=. help2man --no-info --include=doc/man-sparkd.txt --name="The Sparked application launcher" ./bin/sparkd --output=doc/sparkd.1',
        ]
    if os.path.exists("doc/man-sparkd.txt"):
        try:
            help2man = procutils.which("help2man")[0]
        except IndexError:
            print("Cannot build the man pages. help2man was not found.")
        else:
            for c in commands:
                print("$ %s" % (c))
                subprocess.call(c, shell=True)



setup(
    name = "Sparked",
    version = sparked.__version__,
    author = "Arjan Scherpenisse",
    author_email = "arjan@scherpenisse.net",
    url = "http://scherpenisse.net/sparked",
    description = "Application development framework for interactive installations",
    scripts = [
        "bin/sparkd"
        ],
    license="MIT/X",
    packages = ['sparked',
                'sparked.hardware',
                'sparked.internet',
                'sparked.graphics',
                'sparked.test',
                'twisted.plugins'],
    package_data={'twisted.plugins': ['twisted/plugins/sparked.py']},

    long_description = """
Like Twisted, Sparked is a python library and an application runner in once. Some of its features follow here:

 * Robust startup and restart of the program; if it crashes, it's started again.
 * Logging: keeps a rotated logfile for debugging purposes.
 * Pidfile management for making sure your app starts only once.
 * A GUI status window (based on GTK) for monitoring the state of the application and the state of the system (network, power supply, ...). Easy to add your own monitors.
 * Fullscreen graphics display for creating interactive displays, based on the clutter library.
 * Eventing system for broadcasting messages between spark modules.
 * A state machine for guiding the application through different states, with callback functions.

    """,
      install_requires = [
      'Twisted>=8.0'
      ],
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
