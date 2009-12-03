import os
from os.path import splitext, getmtime, isfile
from pyflu.setuptools.base import CommandBase
from pyflu.path import iter_files
from setuptools import setup, find_packages, Extension


class CompileCythonCommand(CommandBase):
    
    description = "compile all cython files"
    user_options = [
           ("include=", "I", ".pxi include directories (separated by ',')"),
           ("cplus", None, "compile to c++ (default: False)"),
        ]

    boolean_options = ["cplus"]

    defaults = {
            "include": "",
            "cplus": False,
        }

    def run(self):
        for infile in self.cython_files():
            outfile = splitext(infile)[0] + self.outfiles_ext()
            if isfile(outfile) and getmtime(infile) <= getmtime(outfile):
                # Source is older than compiled output, skip it
                continue
            cmd = "cython "
            if self.cplus:
                cmd += "--cplus "
            if self.include:
                cmd += "-I %s " % self.include
            cmd += infile
            print cmd
            os.system(cmd)

    def outfiles_ext(self):
        if self.cplus:
            return ".cpp"
        return ".c"

    @classmethod
    def cython_files(cls):
        return iter_files(".pyx")

    @classmethod
    def extensions(cls, include_dirs, libraries, library_dirs, cplus=None,
            additional_sources={}):
        if cplus is None:
            cplus = cls.defaults.get("cplus", False)
        if cplus:
            ext_ext = ".cpp"
        else:
            ext_ext = ".c"
        ret = []
        for path in cls.cython_files():
            base, ext = splitext(path)
            ext_path = base + ext_ext
            module_name = base.replace(os.sep, ".")
            while module_name.startswith("."):
                module_name = module_name[1:]
            add_srcs = additional_sources.get(module_name, [])
            ret.append(Extension(module_name, [ext_path] + add_srcs,
                include_dirs=include_dirs,
                libraries=libraries,
                library_dirs=library_dirs))
        return ret


