#!/usr/bin/env python

import sys
import os

try:
    from setuptools import setup
    setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

VERSION = "0.1.1"

setup(
    name="arango",
    version=VERSION,
    description="Driver for ArangoDB",
    author="Max Klymyshyn",
    author_email="klymyshyn@gmail.com",
    url="http://arangodb-python-driver.readthedocs.org/en/latest/",
    packages=["arango"],
    long_description=open("README.md").read(),
    package_data={'': ['LICENSE']},
    include_package_data=True,
    data_files=[
        ("./", ["README.md"]),
    ],
    install_requires=["nose", "mock", "pycurl"],
    test_suite="nose",
    classifiers=[
        "Topic :: Database",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7"
    ]
)
