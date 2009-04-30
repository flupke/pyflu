from pyflu.setuptools.base import CommandBase
from pyflu.modules import deep_import
from pyflu.command import run_script
import os
from os.path import join
import tarfile
import tempfile
import shutil
import re


class VersionCommandBase(CommandBase):
    """
    Base class for commands that manipulate version.
    """

    user_options = [
            ("version-path=", None, "path of the file containing the "
                "version() function, relative to --from-path"),
        ]
    defaults = {
            "version_path": None,
        }

    def write_version(self, dst_dir, version):
        """
        Write the version to a release export.

        This implementations writes a simple version() function at the end the
        file pointed by self.version_path.
        """
        path = join(dst_dir, self.version_path)
        f = open(path, "a")
        f.write("\ndef version(): return %s\n" % repr(version))
        f.close()
    

class SVNReleaseCommand(VersionCommandBase):
    user_options = [
            ("svn", None, "make a subversion snapshot"),
            ("release", None, "make a normal release"),
            ("svn-url=", None, "subversion repository URL"),
            ("tags-path=", None, "subversion tags path from the base url"),
            ("from-path=", None, "create releases from this subversion path"),
            ("name=", None, "name of the release"),
            ("svn-executable=", None, "path to the subversion executable"),
            ("version=", None, "version to use for normal releases"),
            ("copy-to=", None, "copy the resulting archive to the given "
                "path with scp"),
        ]

    defaults = {
            "svn": False,
            "release": False,
            "svn_url": None,
            "tags_path": "tags",
            "from_path": None,
            "name": None,
            "svn_executable": "/usr/bin/svn",
            "version": None,
            "copy_to": None
        }

    boolean_options = ["svn", "release"]

    def finalize_options(self):
        # Verify options
        if self.svn_url is None:
            raise ValueError("you must specify the subversion repository URL "
                    "with --svn-url")
        if not self.svn and not self.release:
            raise ValueError("you must specify either --release or --svn")
        if self.from_path is None:
            raise ValueError("you must specify the source svn path with "
                    "--from-path")
        if self.name is None:
            raise ValueError("you must specify the target name with --name")
        # Verify dependant options
        if self.release and self.version is None:
            raise ValueError("you must specify a --version for normal "
                    "releases")
        # Generate default values
        if self.version_path is None:
            self.version_path = join(self.name, "__init__.py")
        # Some handy variables
        self.tags_url = join(self.svn_url, self.tags_path)
        self.src_url = join(self.svn_url, self.from_path)

    def run(self):
        work_dir = tempfile.mkdtemp()
        try:
            # Extract code
            print "retrieving code from %s..." % self.src_url
            dst_dir = join(work_dir, self.name)
            output = run_script("%s export %s %s" % (self.svn_executable, 
                self.src_url, dst_dir), pipe_output=True)
            if self.svn:
                # Get revision number
                last_line = output[0][0].split("\n")[-2]
                rev = re.search("(\d+)", last_line).group(0)
                version = "r%s" % rev
                print "extracted svn revision %s" % rev
            elif self.release:
                version = self.version
            # Write version
            self.write_version(dst_dir, version)
            # Create archive
            try:
                os.mkdir("dist")
            except OSError:
                pass
            tar_path = join("dist", "%s-%s.tar.gz" % (self.name, version))
            tar = tarfile.open(tar_path, "w:gz")
            tar.add(dst_dir, "%s-%s" % (self.name, version))
            tar.close()
            print "created archive %s" % tar_path
            # Upload            
            if self.copy_to is not None:
                print "Copying to %s..." % self.copy_to
                run_script("scp %s %s" % (tar_path, self.copy_to))
        finally:
            shutil.rmtree(work_dir)

