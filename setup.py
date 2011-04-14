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


if "doc" in sys.argv:
    os.system("mkdir -p doc/api && epydoc --html -o doc/api/ sparked")
    del sys.argv[sys.argv.index("doc")]

if "build" in sys.argv:
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
                'sparked.web',
                'twisted.plugins'],
    package_data={'twisted.plugins': ['twisted/plugins/sparked.py'],
                  'sparked.web': ['*.js']},

    long_description = open(os.path.join(os.path.dirname(__file__), "README"), "r").read(),
    install_requires = [
      'Twisted>=9.0'
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
