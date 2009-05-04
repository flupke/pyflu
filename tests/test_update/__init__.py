import os
from os.path import dirname, join, isdir, isfile
from pyflu.update import patch, diff, sub_path, control_sum, \
        InvalidOriginalFile, InvalidResultingFile, IncompatiblePatchFormat, \
        archive_path
import shutil


data_dir = join(dirname(__file__), "data")
orig_dir = join(data_dir, "orig")
bad_orig_dir = join(data_dir, "bad_orig")
new_dir = join(data_dir, "new")
tmp_dir = join(data_dir, "tmp")
patch_file = join(data_dir, "patch.tar.bz2")
bad_patch_file = join(data_dir, "bad_patch.tar.bz2")
incompatible_patch_file = join(data_dir, "incompatible_patch.tar.bz2")


def one_way_compare(d1, d2, visited):
    for base, dirs, files in os.walk(d1):
        sub_dir = sub_path(base, d1)
        for file in files:
            sub_file = join(sub_dir, file)
            f1 = join(d1, sub_file)
            f2 = join(d2, sub_file)
            if sub_file in visited:
                continue
            assert isfile(f2)
            assert control_sum(f1) == control_sum(f2)
            visited[sub_file] = None


def compare_directories(d1, d2):
    visited = {}
    one_way_compare(d1, d2, visited)
    one_way_compare(d2, d1, visited)


def test_utilities():
    # sub_path()
    a = "abc/def/file.txt"
    base = "abc"
    assert sub_path(a, base) == "def/file.txt"
    # archive_path()
    assert archive_path("a", r"b\\c\d", "e") == "a/b/c/d/e"


def test_basic():
    def dummy_start(stage, length):
        pass
    def dummy_progress(index):
        pass
    diff(patch_file, orig_dir, new_dir)
    patch(patch_file, orig_dir, tmp_dir, dummy_start, dummy_progress)
    compare_directories(new_dir, tmp_dir)


def test_error():
    diff(patch_file, orig_dir, new_dir)
    # Invalid patched dir
    try:
        patch(patch_file, bad_orig_dir, tmp_dir)
    except InvalidOriginalFile, e:
        str(e)
        pass
    else:
        raise AssertionError("InvalidOriginalFile not raised")
    # Invalid patch file
    try:
        patch(bad_patch_file, orig_dir, tmp_dir)
    except InvalidResultingFile:
        pass
    else:
        raise AssertionError("InvalidResultingFile not raised")
    # Incompatible patch file
    try:
        patch(incompatible_patch_file, orig_dir, tmp_dir)
    except IncompatiblePatchFormat:
        pass
    else:
        raise AssertionError("IncompatiblePatchFormat not raised")


def teardown():
    if isdir(tmp_dir):
        shutil.rmtree(tmp_dir)
    if isfile(patch_file):
        os.unlink(patch_file)
    
