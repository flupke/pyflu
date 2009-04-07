#!/usr/bin/env python

from setuptools import setup, find_packages, Extension
from pyflu import version
from pyflu.setuptools.versioning import GitReleaseCommand


class PyfluReleaseCommand(GitReleaseCommand):
    defaults = {
        "version": version(),
        "name": "pyflu",
    }


setup(
    name = "pyflu",
    version = version(),
    author = "Luper Rouch",
    author_email = "luper.rouch@gmail.com",

    packages = find_packages(),    
    cmdclass = {
        "release": PyfluReleaseCommand,
    },    
)
