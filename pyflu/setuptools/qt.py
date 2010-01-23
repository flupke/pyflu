"""
The CompilePyQtCommand class can be used to ease compilation of .ui and .qrc
files.

Sample setuptools script:

#!/usr/bin/env python
from setuptools import setup, find_packages, Extension
from pyflu.setuptools.qt import CompilePyQtCommand


class MyPyQtCommand(CompilePyQtCommand):

    defaults = {
            "ui_dirs": "files/gui",
            "output_dir": "myapp/gui/ui",
            "widgets_dir": "myapp/gui/widgets",
            "dialogs_dir": "myapp/gui/dialogs",
            "default_dir": "myapp/gui",
        }


setup(
    # Usual setuptools/distutils stuff

    cmdclass = {
        "qtcompile": MyPyQtCommand,
    },
)
"""


from pyflu.modules import deep_import
from pyflu.setuptools.base import CommandBase
import os
from os.path import splitext, join, getmtime
import inspect


class CompilePyQtCommand(CommandBase):
    user_options = [
            ("create-classes", "c", "create classes skeletons"),
            ("ui-dirs=", "u", "comma separated list of .ui and .qrc folders"),
            ("output-dir=", "o", "put compiled files in this folder"),
            ("widgets-dir=", "w", "create widget skeletons in this folder"),
            ("dialogs-dir=", "d", "create dialog skeletons in this folder"),
            ("default-dir=", None, "create other skelettons in this folder"),
        ]
    boolean_options = ["create-classes"]
    defaults = {
            "create_classes": False,
        }
    description = "compile PyQt interface files"
    skeletons_template = """from PyQt4.QtGui import *
from PyQt4.QtCore import *    
from %(ui_module)s import *


class %(class_name)s(%(qt_base)s, %(ui_class)s):

    def __init__(self, parent=None):
        %(qt_base)s.__init__(self, parent)
        %(ui_class)s.__init__(self)
        self.setupUi(self)


__all__ = ["%(class_name)s"]
"""

    def finalize_options(self):
        self.ui_dirs = [x.strip() for x in self.ui_dirs.split(",") 
                if x.strip()]

    def iter_files(self, folder, target_ext):
        for file in os.listdir(folder):
            name, ext = splitext(file)
            if ext != target_ext:
                continue
            yield join(folder, file), name

    def run_command(self, cmd):
        print cmd
        os.system(cmd)

    def ask_qt_base(self, infile):
        name = raw_input("What is the Qt base class for UI file '%s' ? "
                "[QDialog] " % infile)
        if not name:
            return "QDialog"
        return name

    def run(self):
        # Compile
        for folder in self.ui_dirs:
            for infile, name in self.iter_files(folder, ".qrc"):
                outfile = join(self.output_dir, name + "_rc.py")
                if not os.path.isfile(outfile) or \
                        getmtime(infile) > getmtime(outfile):
                    self.run_command("pyrcc4 %s -o %s" % (infile, outfile))
            for infile, name in self.iter_files(folder, ".ui"):
                outfile = join(self.output_dir, name + ".py")
                if not os.path.isfile(outfile) or \
                        getmtime(infile) > getmtime(outfile):
                    self.run_command("pyuic4 %s -o %s" % (infile, outfile))
        # Create missing classes skeletons
        if not self.create_classes:
            return
        for folder in self.ui_dirs:
            for infile, name in self.iter_files(folder, ".ui"):
                # Skip if there is already a file defined
                if name.endswith("_widget"):
                    target = join(self.widgets_dir, 
                            name[:-len("_widget")] + ".py")
                elif name.endswith("_dialog"):
                    target = join(self.dialogs_dir, 
                            name[:-len("_dialog")] + ".py")
                else:
                    target = join(self.default_dir, name + ".py")
                if os.path.isfile(target):
                    continue
                # Create class skeleton                
                if name.endswith("_dialog"):
                    qt_base = "QDialog"
                elif name.endswith("_widget"):
                    qt_base = "QWidget"
                else:
                    qt_base = self.ask_qt_base(infile)
                ui_module_path = "%s.%s" % (self.output_dir.replace("/", "."), name)
                ui_module = deep_import(ui_module_path)
                ui_classes = [x[1] for x in inspect.getmembers(ui_module) if 
                        inspect.isclass(x[1]) and
                        x[1].__name__.startswith("Ui_")]
                if len(ui_classes) != 1:
                    raise Exception("found more than one class in the UI file "
                            "'%s'" % infile)
                skel = self.skeletons_template % {                       
                    "qt_base": qt_base,
                    "ui_module": ui_module_path,
                    "ui_class": ui_classes[0].__name__,
                    "class_name": ui_classes[0].__name__[3:],
                }
                print "Creating UI skeleton file for '%s'" % name
                open(target, "w").write(skel)
