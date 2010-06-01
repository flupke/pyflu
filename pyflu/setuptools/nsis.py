import os
from pyflu.setuptools.base import CommandBase
from pyflu.command import run_script
from pyflu.path import sub_path


class CompileNsisCommand(CommandBase):
    """
    Create and compile an NSIS installer script from a template.
    """

    user_options = [
            ("nsis-template", None, "NSIS Installer template file."),
            ("nsis-compiler", None, "NSIS compiler path."),
            ("script-output", None, "Compiled script file."),
        ]

    defaults = {
            "nsis_compiler": "makensis.exe",
            "script_output": "installer.nsi",
        }

    input = [ ]
    """
    List of input directories.

    Each entry is a tuple: (type, input, output_dir)

    ``type`` is a string indicating the entry type : 'd' for a directory, 'f'
    for a file. ``input`` is the file or directory input and ``output_dir``
    the output directory, relative to the installation directory.
    """

    version = "0.1_pre"

    def run(self):
        script_file = open(self.script_output, "w")
        template_file = open(self.nsis_template, "r")
        data = { 
                "version": self.version,
            }
        # Build input files list
        files = []
        for etype, input, output in self.input:
            if etype == "d":
                self.append_tree(input, output, files)
            elif etype == "f":
                print os.path.basename(input), output
                files.append((os.path.join(output, os.path.basename(input)), 
                        input))
        data["install_files"] = "\n".join([
            'SetOutPath "$INSTDIR\%s"\nFile "%s"' %
            (os.path.dirname(e[0]), e[1]) for e in files])
        data["uninstall_files"] = "\n".join(
                ['Delete "$INSTDIR\%s"' % e[0] for e in files])
        # Render template
        script_file.write(template_file.read() % data)
        script_file.close()
        # Compile
        run_script("%s %s" % (self.nsis_compiler, self.script_output))

    def append_tree(self, dir, output, files_list):
        for base, dirs, files in os.walk(dir):
            sub_dir = sub_path(base, dir)
            for file in files:
                files_list.append((os.path.join(output, sub_dir, file), 
                    os.path.join(base, file)))
