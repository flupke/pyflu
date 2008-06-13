#!/usr/bin/env python

from setuptools import setup, find_packages, Extension
from pyflu import version


setup(
    name = "pyflu",
    version = version(),
    author = "Luper Rouch",
    author_email = "luper.rouch@gmail.com",

    packages = find_packages(exclude=["palette.bin"]),    
    scripts = ["palette/bin/run-palette.py"],

    install_requires = ["louie"],
    install_requires = ["pygame"],
    ext_modules = [fractal_plane_module]
)
