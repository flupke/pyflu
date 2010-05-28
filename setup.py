#!/usr/bin/env python

from setuptools import setup, find_packages, Extension
from pyflu import version


setup(
    name = "pyflu",
    version = version(),
    author = "Luper Rouch",
    author_email = "luper.rouch@gmail.com",
    maintainer = "Luper Rouch",
    maintainer_email = "luper.rouch@gmail.com",
    url = "http://projects.luper.fr/misc/wiki/pyflu",
    description = "A collection of Python utilities.",
    long_description = 
"""Helpers for standard Python modules, things that I frequently use in
my projects and find useful.

The ``update`` package depends on bsdiff_. Ubuntu users can find it in the
``python-bsdiff`` package.

.. _bsdiff: http://starship.python.net/crew/atuining/cx_bsdiff/index.html
""",
    classifiers = [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],

    setup_requires = ["nose"],
    install_requires = ["lxml"],

    packages = find_packages(exclude="tests"),
)
