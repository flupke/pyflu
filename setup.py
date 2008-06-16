#!/usr/bin/env python

from setuptools import setup, find_packages, Extension
from pyflu import version


setup(
    name = "pyflu",
    version = version(),
    author = "Luper Rouch",
    author_email = "luper.rouch@gmail.com",

    packages = find_packages(),    
)
