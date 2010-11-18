import os
import shutil
import louie
from os.path import abspath, join, dirname, isdir
from mock import Mock
from PyQt4.QtGui import *
from PyQt4.QtTest import QTest
from pyflu.update.qt import UpdateDialogMixin
from pyflu.qt.util import get_or_create_app
from pyflu.tests.test_update import data_dir, tmp_dir, one_way_compare
from pyflu.update import signals


work_dir = join(tmp_dir, "test_qt_work_dir")
target_dir = join(work_dir, "target")


class Ui_UpdateDialog(object):

    def setupUi(self, StartupDialog):
        self.verticalLayout = QVBoxLayout(StartupDialog)
        self.operation_label = QLabel(StartupDialog)
        self.verticalLayout.addWidget(self.operation_label)
        self.progress_bar = QProgressBar(StartupDialog)
        self.verticalLayout.addWidget(self.progress_bar)


class UpdateDialog(UpdateDialogMixin, QDialog, Ui_UpdateDialog):

    update_url = "file://%s" % abspath(join(data_dir, "patches", "index.html"))
    version_pattern = r"(?P<%s>r?[0-9a-zA-Z_.-]+?)"
    patch_files_pattern = r"^patch-%s-%s\.tar\.bz2" % \
            (version_pattern % "from", version_pattern % "to")
    current_version = "1.0"
    patch_dl_dir = work_dir
    patch_target_dir = join(work_dir, "target")

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)


def test_update_dialog():

    def finish_update(patched_dir):
        "Post patch signal handler"
        shutil.rmtree(UpdateDialog.patch_target_dir)
        os.rename(patched_dir, UpdateDialog.patch_target_dir)

    # Copy version 1.0 to the work dir
    shutil.copytree(join(data_dir, "patches", "versions", "1.0"), target_dir)
    # Apply patches
    app = get_or_create_app()
    dlg = UpdateDialog()
    dlg._exit = Mock()
    dlg._exit.side_effect = lambda code: dlg.close()
    louie.connect(finish_update, signals.update_finished, dlg)
    dlg.start_update(confirm=False)    
    app.exec_()
    # We should now be at version 1.1
    v1_1_dir = join(data_dir, "patches", "versions", "1.1")
    one_way_compare(v1_1_dir, target_dir)


def setup():
    if isdir(work_dir):
        shutil.rmtree(work_dir)
    os.makedirs(work_dir)

