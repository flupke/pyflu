import sys
import os
import hashlib
from os.path import join, commonprefix, isfile, isdir, dirname, basename
from pyflu.path import sub_path
import bsdiff
import tarfile
import pickle
import struct
import shutil
from StringIO import StringIO


__version__ = "0.1"


class UpdateError(Exception): pass

class InvalidFile(UpdateError): 
    def __init__(self, path):
        self.path = path
    def __str__(self):
        return "'%s'" % self.path

class InvalidOriginalFile(InvalidFile): pass
class InvalidResultingFile(InvalidFile): pass
class IncompatiblePatchFormat(UpdateError): pass


class PatchInfo(object):

    def __init__(self):
        self.control_sums = {}
        self.version = __version__

    def store_sums(self, path, orig_file, new_file):
        """Store control sums of original and new files"""
        self.control_sums[path] = (control_sum(orig_file),
                control_sum(new_file))

    def valid_orig(self, path, file):
        """
        Returns True if ``file`` has the same control sum as the original 
        file stored under ``path`` in this patch info object.
        """
        return self.control_sums[path][0] == control_sum(file)

    def valid_result(self, path, file):
        """
        Returns True if ``file`` has the same control sum as the new 
        file stored under ``path`` in this patch info object.
        """
        return self.control_sums[path][1] == control_sum(file)

    def is_ext_file(self, path):
        """
        Returns True if the file at ``path`` is external to the patch.
        """
        return path not in self.control_sums

    def __setstate__(self, state):
        self.__dict__.update(state)
        if self.version != __version__:
            raise IncompatiblePatchFormat("patch file has version '%s', "
                    "the library can read version '%s'" % 
                    (self.version, __version__))


class PatchFile(object):
    """
    Utility class to read and write patches in a TarFile object.

    Patches are stored in a simple binary format that should be compressed
    efficiently.
    """
    
    patches_prefix = "patches"
    plain_prefix = "plain"
    info_path = "info"

    header_fmt = "<q"
    block_header_fmt = "<q"
    block_data_fmt_pattern = "<%ds"

    def __init__(self, tar):
        self.tar = tar

    def diff(self, old_dir, new_dir):
        """
        Fill the TarFile with the differences between two directories.
        """
        self.info = PatchInfo()

        # Write patches and plain files
        for base, dirs, files in os.walk(old_dir):
            sub_dir = sub_path(base, old_dir)
            new_sub_dir = join(new_dir, sub_dir)    
            if not os.path.isdir(new_sub_dir):
                # Directory not present in the new version, simply don't 
                # include it in the patch
                continue
            # Create files diffs
            for file in files:
                old_file = join(base, file)
                new_file = join(new_sub_dir, file)
                if isfile(new_file):
                    # File is present on both sides, store binary diff
                    self.store_diff(self.patch_path(sub_dir, file), 
                            old_file, new_file)
            # Search for new files and directories
            for item in os.listdir(new_sub_dir):
                item_path = join(new_sub_dir, item)
                if isfile(item_path):
                    if item not in files:
                        self.tar.add(item_path, 
                                self.plain_path(sub_dir, item))
                elif isdir(item_path):
                    if item not in dirs:
                        self.tar.add(item_path, 
                                self.plain_path(sub_dir, item))

        # Write info file
        data = pickle.dumps(self.info)
        info = tarfile.TarInfo(self.info_path)
        info.size = len(data)
        self.tar.addfile(info, StringIO(data))

    def patch(self, old_dir, dest_dir, start_callback=None, 
            progress_callback=None):
        """
        Apply the patch to the content of ``old_dir`` and write the results in
        ``dest_dir``.
        """
        # Read info file
        self.info = pickle.load(self.tar.extractfile(self.info_path))

        # Patch files
        if start_callback is not None:
            # Count source files
            length = 0
            for base, dirs, files in os.walk(old_dir):
                length += len(files)
            start_callback(stage="patch", length=length)  
        index = 0
        for base, dirs, files in os.walk(old_dir):
            sub_dir = sub_path(base, old_dir)
            dest_sub_dir = join(dest_dir, sub_dir)
            # Make directory if it does not exists yet
            if not isdir(dest_sub_dir):
                os.makedirs(dest_sub_dir)
            for file in files:
                patch_path = self.patch_path(sub_dir, file)
                src_file = join(base, file)
                dst_file = join(dest_sub_dir, file)
                if self.info.is_ext_file(patch_path):
                    # File is not in the patch, copy it to the destination dir
                    shutil.copy(src_file, dst_file)
                else:
                    self.patch_file(src_file, dst_file, patch_path)
                if progress_callback is not None:
                    index += 1
                    progress_callback(index=index)

        # Extract plain files
        plain_files = [m for m in self.tar.getmembers() 
                if m.name.startswith(self.plain_prefix)
                and not m.isdir()]
        if start_callback is not None:
            start_callback(stage="plain", length=len(plain_files))
        index = 0
        for file in plain_files:
            outpath = join(dest_dir, 
                    sub_path(file.name, self.plain_prefix))
            outdir = dirname(outpath)
            if not isdir(outdir):
                os.makedirs(outdir)
            infile = self.tar.extractfile(file)
            outfile = open(outpath, "wb")
            while True:
                data = infile.read(2**14)
                if not data:
                    break
                outfile.write(data)
            outfile.close()
            if progress_callback is not None:
                index += 1
                progress_callback(index=index)

    def store_diff(self, tar_path, old_file, new_file):
        """
        Stores the diff of two files in the internal TarFile.
        
        The patch is stored in the TarFile object at ``tar_path``, and
        is constructed from the contents of the files ``old_file`` and
        ``new_file``.

        The sums dictionnary is also updated.
        """
        # Compute files sums
        self.info.store_sums(tar_path, old_file, new_file)
        # Compute files diff
        old_content = open(old_file, "rb").read()
        new_content = open(new_file, "rb").read()
        ctrl, diff_block, extra_block = bsdiff.Diff(old_content, new_content)
        ctrl_block = pickle.dumps(ctrl)
        # Prepare struct format
        fmt = self.header_fmt
        fmt += self.block_fmt(ctrl_block)
        fmt += self.block_fmt(diff_block)
        fmt += self.block_fmt(extra_block)
        # Pack data and write it to the TarFile
        data = struct.pack(fmt, 
                len(new_content), 
                len(ctrl_block), ctrl_block,
                len(diff_block), diff_block, 
                len(extra_block), extra_block)
        info = tarfile.TarInfo(tar_path)
        statinfo = os.stat(new_file)
        info.size = len(data)
        info.mode = statinfo.st_mode
        info.mtime = statinfo.st_mtime
        self.tar.addfile(info, StringIO(data))

    def patch_file(self, orig_path, dest_path, patch_path):
        """
        Patch a file.

        Patches the file at ``orig_path`` into ``dest_path`` with patch info
        stored in the TarFile at ``patch_path``.
        """
        # First check file to be patched
        if not self.info.valid_orig(patch_path, orig_path):
            raise InvalidOriginalFile(orig_path)
        # Open files
        orig = open(orig_path, "rb")
        dest = open(dest_path, "wb")
        patch_info = self.tar.getmember(patch_path)        
        patch_data = self.tar.extractfile(patch_info).read()
        offset = 0
        # Parse patch header
        new_content_len = struct.unpack_from(self.header_fmt, patch_data)[0]
        offset += struct.calcsize(self.header_fmt)
        # Get data blocks
        offset, ctrl_block = self.read_block(patch_data, offset)
        ctrl = pickle.loads(ctrl_block)
        offset, diff_block = self.read_block(patch_data, offset)
        offset, extra_block = self.read_block(patch_data, offset)
        # Construct new file
        dest.write(bsdiff.Patch(orig.read(), new_content_len, 
                ctrl, diff_block, extra_block))
        # Close files
        dest.close()
        orig.close()
        # Restore file's mode
        os.chmod(dest_path, patch_info.mode)
        # Check resulting file validity
        if not self.info.valid_result(patch_path, dest_path):
            raise InvalidResultingFile(dest_path)

    def block_fmt(self, data):
        """Returns the struct format string for a data block"""
        fmt = self.block_header_fmt
        fmt += (self.block_data_fmt_pattern % len(data))[1:]
        return fmt[1:]

    def read_block(self, data, offset):
        """Read a data block, returns new offset in data and block data"""
        data_len = struct.unpack_from(self.block_header_fmt, data, offset)[0]
        offset += struct.calcsize(self.block_header_fmt)
        data_fmt = self.block_data_fmt_pattern % data_len
        data = struct.unpack_from(data_fmt, data, offset)[0]
        offset += struct.calcsize(data_fmt)
        return offset, data

    # Utilities 

    def patch_path(self, path, file):
        return archive_path(self.patches_prefix, path, file)

    def plain_path(self, path, file):
        return archive_path(self.plain_prefix, path, file)


def diff(patch_file, old_dir, new_dir):
    """
    Create a patch file storing the differences between ``old_dir`` and
    ``new_dir``.
    """
    tar = tarfile.open(patch_file, "w:bz2")
    patch = PatchFile(tar)
    patch.diff(old_dir, new_dir)
    tar.close()


def patch(patch_file, old_dir, dest_dir, start_callback=None,
        progress_callback=None):
    """
    Patch ``old_dir`` with ``patch_file`` into ``dest_dir``.

    Optional arguments ``start_callback`` and ``progress_callback`` can be
    specified to handle notifications of progress.
    
    ``start_callback`` must be a callable taking the keyword arguments
    ``stage`` and ``length``, it will be called at each stage of the patching
    process. The patching process consists of two stages : "patch" where
    existing files are patched and "plain" where new files are extracted. The
    ``length`` argument indicates how many files are going to be processed.
    
    ``progress_callback`` is a callable taking a single keyword argument,
    ``index`` wich indicates the progression of each stage (takes values
    between 1 and ``length``).    
    """
    tar = tarfile.open(patch_file, "r:bz2")
    patch = PatchFile(tar)
    patch.patch(old_dir, dest_dir, start_callback, progress_callback)
    tar.close()


def archive_path(prefix, path, file):
    """
    Returns a path in an archive, formed by concatenating ``prefix``,
    ``path`` and ``file``.
    """
    ret = join(prefix, path, file)
    return ret.replace("\\", "/").replace("//", "/")


def control_sum(fpath):
    """Returns the control sum of the file at ``fpath``"""
    f = open(fpath, "rb")
    digest = hashlib.sha512()
    while True:
        buf = f.read(4096)
        if not buf:
            break
        digest.update(buf)
    f.close()
    return digest.digest()


def usage():
    print "usage: %s [diff|patch] [dest] [orig] [new]" % sys.argv[0]


def makepatch():
    """
    Entry points for the create patch command line script.
    """
    try:
        olddir, newdir, patchfile = sys.argv[1:]
    except:
        print >>sys.stderr, ("usage: %s olddir newdir patchfile" 
                % basename(sys.argv[0]))
        sys.exit(1)
    diff(patchfile, olddir, newdir)
    sys.exit(0)
