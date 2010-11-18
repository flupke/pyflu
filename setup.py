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

The ``update`` package depends on bsdiff_ and lxml. They can be found in the
Debian packages ``python-bsdiff`` and ``python-lxml``.

.. _bsdiff: http://starship.python.net/crew/atuining/cx_bsdiff/index.html
""",
    classifiers = [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],

    packages = find_packages(),

    entry_points = {
        "console_scripts": ["pyflu-makepatch = pyflu.update:makepatch"],
    },
)
