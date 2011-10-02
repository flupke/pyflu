from os.path import basename, join, dirname, isdir
import os
import sys
import shutil
import re
import louie
import urllib2
from PyQt4.QtGui import *
from PyQt4.QtCore import *    
from PyQt4.QtNetwork import *
from pyflu.update import patch, signals
from pyflu.command import run_script
from pyflu.update.remote import find_patches_groups
from pyflu.update.version import Version


class UpdateDialogMixin(object):
    """
    A mixin class used for update dialogs.

    It should be used with a QDialog-derived class containing a label and a
    progress bar widget, to display long operations progression.

    Class parameters that need to be redefined in subclasses:
      * *update_url*
      * *patch_files_pattern*, the regular expression object used to retrieve
        patch files on the *update_url* page
      * *current_version*: the current version string
      * *patch_dl_dir*: the temporary directory where patches are downloaded
      * *patch_target_dir*: the directory to patch
    """

    _properties = ["update_url", "patch_files_pattern"]

    update_url = None
    version_pattern = r"(?P<%s>r?[0-9a-zA-Z_.-]+?)"
    patch_files_pattern = r"^patch-%s-%s\.tar\.bz2" % \
            (version_pattern % "from", version_pattern % "to")
    current_version = None
    patch_dl_dir = None
    patch_target_dir = None
    progress_bar_name = "progress_bar"
    operation_label_name = "operation_label"

    def start_update(self, confirm=True):
        """
        Shows the dialog and starts the update process.

        If *confirm* is True, a confirmation dialog is shown before starting
        the update. The :class:`~pyflu.update.signals.not_updated` signal is
        sent if no update was performed (either because there was no update
        available or the user refused to apply it).
        """
        # Check for updates
        self.patches_paths = []
        self.start_long_operation(
                self.trUtf8("Searching for updates..."), 1)
        self.download_queue = self._updates_urls()
        self.update_long_operation(1)
        if self.download_queue:
            # Updates available, apply them or exit
            if confirm:
                ret = QMessageBox.question(self, 
                        self.trUtf8("Updates available"),
                        self.trUtf8("Updates were found, do you want to "
                            "install them now ?"),
                        QMessageBox.Ok | QMessageBox.Abort)
                do_update = ret == QMessageBox.Ok
            else:
                do_update = True
            if do_update:
                self._download_next()
                return
        louie.send(signals.not_updated, self)

    def start_long_operation(self, text, length):
        pb = getattr(self, self.progress_bar_name)
        ol = getattr(self, self.operation_label_name)
        ol.setText(text)
        pb.setValue(0)
        pb.setRange(0, length)
        QCoreApplication.processEvents()

    def update_long_operation(self, index):
        pb = getattr(self, self.progress_bar_name)
        pb.setValue(index)
        QCoreApplication.processEvents()

    def _download_next(self):
        pb = getattr(self, self.progress_bar_name)
        ol = getattr(self, self.operation_label_name)
        # Open download file object
        self.download_url = self.download_queue.pop(0)        
        fname = basename(self.download_url)
        self.save_path = join(self.patch_dl_dir, fname)
        ol.setText(self.trUtf8("Downloading '%1'").arg(fname))
        pb.setValue(0)
        self.file = QFile(self.save_path)
        self.file.open(QFile.ReadWrite)
        # Start download
        manager = QNetworkAccessManager(self)
        self.reply = manager.get(QNetworkRequest(QUrl(self.download_url)))
        self.reply.downloadProgress.connect(self._update_download_progress)
        self.reply.error.connect(self._download_error)
        self.reply.readyRead.connect(self._flush_download)
        self.reply.finished.connect(self._download_finished)

    def _update_download_progress(self, received, total):
        pb = getattr(self, self.progress_bar_name)
        pb.setRange(0, total)
        pb.setValue(received)

    def _flush_download(self):
        self.file.write(self.reply.readAll())

    def _download_error(self, code):
        QMessageBox.critical(self, self.trUtf8("Error"), 
                self.trUtf8("An error happened while downloading %1: %2")
                .arg(self.download_url)
                .arg(code))
        self._exit(1)

    def _download_finished(self):
        self.file.close()
        self.patches_paths.append(self.save_path)
        if self.download_queue:
            # Start next download
            self._download_next()
        else:
            # All has been downloaded
            old_dir = self.patch_target_dir
            # Create target directory(ies)
            new_dir = old_dir + "_"
            while isdir(new_dir):
                new_dir += "_"
            os.mkdir(new_dir)
            if len(self.patches_paths) > 1:
                new_dir2 = new_dir + "_"
                while isdir(new_dir2):
                    new_dir2 += "_"
                os.mkdir(new_dir2)
            # Apply patches, starting from original dir to new_dir, then 
            # cycling between new_dir and new_dir2
            d1 = old_dir
            d2 = new_dir
            for patch_index, path in enumerate(self.patches_paths):
                if patch_index == 1:
                    d1 = new_dir
                    d2 = new_dir2
                elif patch_index > 1:
                    d1, d2 = d2, d1
                start_cb, progress_cb = self._patch_callbacks(path, patch_index,
                        len(self.patches_paths))
                patch(path, d1, d2, start_cb, progress_cb)
            # Remove middle-temp dir if we used more than one temp dir
            if d1 != old_dir:
                shutil.rmtree(d1)
            # Remove patch files
            for path in self.patches_paths:
                os.unlink(path)
            # Finish update and quit
            louie.send(signals.update_finished, self, d2)
            self._exit(0)

    def _exit(self, code):
        """
        Simply calls sys.exit() with *code*, allows using the class in unit 
        tests.
        """
        sys.exit(code)

    def _patch_callbacks(self, path, patch_index, total_patches):
        fname = basename(path)

        def start_cb(stage, length):
            if stage == "patch":
                text = self.trUtf8("Installing '%1' (%2/%3) : patching "
                        "files") \
                                .arg(fname) \
                                .arg(patch_index + 1) \
                                .arg(total_patches)
            elif stage == "plain":
                text = self.trUtf8("Installing '%1' (%2/%3) : creating "
                        "new files") \
                                .arg(fname) \
                                .arg(patch_index + 1) \
                                .arg(total_patches)
            self.start_long_operation(text, length)

        def progress_cb(index):
            self.update_long_operation(index)

        return start_cb, progress_cb

    def _updates_urls(self):
        """
        Check for updates on the HTML page pointed by ``url``.
        
        Returns a list of urls pointing to the updates needed to upgrade to the
        latest version.
        """
        try:
            groups = find_patches_groups(self.update_url,
                    re.compile(self.patch_files_pattern))
        except urllib2.HTTPError, err:
            pb = getattr(self, self.progress_bar_name)
            ol = getattr(self, self.operation_label_name)
            pb.setValue(0)
            ol.setText(self.trUtf8("Error opening update url: %1")
                    .arg(unicode(err)))                
        else:
            # Find patches chain entry point
            current_version = Version(self.current_version)
            group = groups.get(current_version, [])
            return [x[2] for x in group]


__all__ = ["StartupDialog"]
