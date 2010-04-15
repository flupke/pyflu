import os
from os.path import splitext, getmtime, isfile
from pyflu.setuptools.base import CommandBase
from pyflu.path import iter_files
from setuptools import setup, find_packages, Extension


class CompileCythonCommand(CommandBase):
    
    description = "compile all cython files"
    user_options = [
           ("include=", "I", "cython include directories (separated by ',')"),
           ("exclude=", "e", "comma separated list of folders to exclude "
                             "from search for .pyx files"),
           ("cplus", None, "compile to c++ (default: False)"),
           ("all", "a", "recompile all cython files (default: False)"),
        ]

    boolean_options = ["cplus", "all"]

    defaults = {
            "include": "",
            "exclude": "",
            "cplus": False,
            "all": False,
        }

    def finalize_options(self):
        self.include = [p for p in self.include.split(",") if p]
        self.exclude = [p for p in self.exclude.split(",") if p]

    def run(self):
        for infile in self.cython_files(exclude=self.exclude):
            outfile = splitext(infile)[0] + self.outfiles_ext()
            if not self.all and \
                    isfile(outfile) and getmtime(infile) <= getmtime(outfile):
                # Source is older than compiled output, skip it
                continue
            cmd = "cython "
            if self.cplus:
                cmd += "--cplus "
            if self.include:
                cmd += "".join(["-I %s " % i for i in self.include])
            cmd += infile
            print cmd
            os.system(cmd)

    def outfiles_ext(self):
        if self.cplus:
            return ".cpp"
        return ".c"

    @classmethod
    def cython_files(cls, exclude=None):
        return iter_files(".pyx", exclude=exclude)

    @classmethod
    def extensions(cls, include_dirs=None, libraries=None, library_dirs=None,
            cplus=None, additional_sources=None, extra_link_args=None,
            extra_compile_args=None, exclude=None):
        if include_dirs is None:
            include_dirs = []
        if libraries is None:
            libraries = []
        if library_dirs is None:
            library_dirs = []
        if cplus is None:
            cplus = cls.defaults.get("cplus", False)
        if cplus:
            ext_ext = ".cpp"
        else:
            ext_ext = ".c"
        if additional_sources is None:
            additional_sources = {}
        if extra_link_args is None:
            extra_link_args = []
        if exclude is None:
            exclude = cls.defaults.get("exclude", "")
            exclude = [e for e in exclude.split(",") if e]
        ret = []
        for path in cls.cython_files(exclude=exclude):
            base, ext = splitext(path)
            ext_path = base + ext_ext
            module_name = base.replace(os.sep, ".")
            while module_name.startswith("."):
                module_name = module_name[1:]
            add_srcs = additional_sources.get(module_name, [])
            ret.append(Extension(module_name, [ext_path] + add_srcs,
                include_dirs=include_dirs,
                libraries=libraries,
                library_dirs=library_dirs,
                extra_link_args=extra_link_args,
                extra_compile_args=extra_compile_args))
        return ret


