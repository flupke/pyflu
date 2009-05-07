from pyflu.setuptools.versioning import VersionCommandBase
import os
from os.path import join, isdir
from pyflu.command import run_script
import pysvn
from pyflu.update import diff


def svn_info(path="."):
    client = pysvn.Client()
    url = client.info(path).url
    info = client.info2(url, recurse=False)[0][1]
    return url, info.rev.number


class CreatePatchCommand(VersionCommandBase):
    """
    Command to create py2exe and py2app patches from subversion checkouts.
    """

    user_options = [
            ("from-version=", None, "From version. Defaults to the last "
                "version found in the patches cache."),
            ("to-version=", None, "To version. Defaults to the latest "
                "subversion release"),
            ("py2exe", "w", "Compile versions using this setup's py2exe "
                "command."),
            ("py2app", "m", "Compile versions using this setup's py2app "
                "command."),
            ("patches-dir=", None, "Directory to store versions used to "
                "construct patches."),
            ("prefix=", None, "Patch files prefix."),
            ("suffix=", None, "Patch files suffix."),
            ("patches-root=", None, "Root of the patched content, relative "
                "to the 'dist' directory of the project."),
            ("verbose-freeze", None, "Verbose output."),
        ]

    defaults = {
            "py2exe": False,
            "py2app": False,
            "patches_dir": "patches-cache",
            "from_version": None,
            "to_version": None,
            "prefix": None,
            "suffix": ".tar.bz2",
            "patches_root": "",
            "verbose_freeze": False,
        }

    boolean_options = ["py2exe", "py2app", "verbose_freeze"]

    subdirs = {
            "svn": "svn",
            "patches": "patches",
        }

    def finalize_options(self):
        if self.py2exe == self.py2app:
            raise Exception("you must specify either --py2app or --py2exe")
        for name, value in self.subdirs.items():
            setattr(self, "%s_subdir" % name, join(self.patches_dir, value))
        if not self.prefix:
            raise Exception("you must specify a --prefix for patch files")
        # Get from_version from the patches cache if no revision was specified
        if not self.from_version:
            if not isdir(self.svn_subdir):
                raise Exception("no patches cache found, --from-version must "
                        "be specified")
            versions = [d for d in os.listdir(self.svn_subdir) 
                    if isdir(join(self.svn_subdir, d))]
            versions.sort(key=lambda x: int(x))
            self.from_version = versions[-1]
        # Get to_version from the HEAD subversion revision number if it was not
        # specified
        self.svn_url, self.head_rev = svn_info()
        if not self.to_version:
            self.to_version = str(self.head_rev)

    def run(self):
        old_path = self.prepare_image(self.from_version)
        new_path = self.prepare_image(self.to_version)
        print "creating patch %s > %s" % (self.from_version, self.to_version)
        if not isdir(self.patches_subdir):
            os.mkdir(self.patches_subdir)
        diff(join(self.patches_subdir, "%s-r%s-r%s%s" % (self.prefix,
            self.from_version, self.to_version, self.suffix)), old_path,
            new_path)

    def prepare_image(self, version):
        svn_dir = join(self.svn_subdir, version)
        frozen_dir = join(svn_dir, "dist")
        text_version = "r%s" % version
        if not isdir(svn_dir):
            self.export(version)
            self.write_version(svn_dir, text_version)
        if not isdir(frozen_dir):
            self.build(svn_dir, text_version)
        self.clean(frozen_dir)
        return join(frozen_dir, self.patches_root)
            
    def export(self, revision):
        print "exporting revision %s" % revision
        dest_path = join(self.svn_subdir, revision)
        client = pysvn.Client()
        client.export(self.svn_url, dest_path,
                revision=self.rev_object(revision))

    def build(self, dir, version):
        run_script("python setup.py %s" % self.freeze_command(), echo=True, 
                cwd=dir, null_output=not self.verbose_freeze)
        self.post_build(dir, version)

    def rev_object(self, rev):
        return pysvn.Revision(pysvn.opt_revision_kind.number, int(rev))

    def freeze_command(self):
        if self.py2exe:
            return "py2exe"
        if self.py2app:
            return "py2app"
        raise ValueError("internal error")

    def clean(self, dir):
        for base, dirs, files in os.walk(dir):
            for file in files:
                if file.endswith(".pyc"):
                    os.unlink(join(base, file))

    def post_build(self, dir, version):
        pass
