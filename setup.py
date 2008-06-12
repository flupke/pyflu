#!/usr/bin/env python

from setuptools import setup, find_packages, Extension
from palette import version


fractal_plane_module = Extension('palette.plugins.fractal_plane_ext',
        sources=['palette/plugins/fractal_plane_ext.cpp'],
        extra_compile_args=["-O2", "-march=i686"])


setup(
    name = "Palette",
    version = version(),
    author = "Luper Rouch",
    author_email = "luper.rouch@gmail.com",

    packages = find_packages(exclude=["palette.bin"]),    
    scripts = ["palette/bin/run-palette.py"],

    install_requires = ["louie"],
    install_requires = ["pygame"],
    ext_modules = [fractal_plane_module]
)
