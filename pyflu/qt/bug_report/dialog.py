import pdb
import thread
from PyQt4.QtGui import QDialog, QDesktopServices
from PyQt4.QtCore import (QUrl, pyqtRestoreInputHook, pyqtRemoveInputHook,
        QCoreApplication)
from pyflu.qt.bug_report.ui_dialog import Ui_BugReportDialog
from pyflu.qt.bug_report.tb import format_html_exception
from pyflu.qt.bug_report import settings


class BugReportDialog(QDialog, Ui_BugReportDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        Ui_BugReportDialog.__init__(self)
        self.setupUi(self)
        self.main_thread_id = thread.get_ident()
        self.reset()
        self.traceback_text.anchorClicked.connect(QDesktopServices.openUrl)
        self.send_button.clicked.connect(self.send_email)
        self.quit_button.clicked.connect(self.reject)
        self.debug_button.clicked.connect(self.debug)
        if not settings.DEV_MODE:
            self.debug_button.hide()
        if not settings.BUG_REPORT_EMAIL:
            self.send_button.hide()

    def reset(self):
        """
        Reset the dialog contents.
        """
        self.threads_tracebacks = {}
        self.main_traceback = None
        self.report_text.clear()
        self.traceback_text.clear()

    def add_tb(self, thread_id, type, value, tb):
        if not self.isVisible():
            self.show()
        if thread_id == self.main_thread_id and self.main_traceback is None:
            self.main_traceback = (type, value, tb)
            self.update_tb_text()
        elif thread_id not in self.threads_tracebacks:
            self.threads_tracebacks[thread_id] = (type, value, tb)
            self.update_tb_text()

    def update_tb_text(self):
        parts = []
        if self.main_traceback is not None:
            parts.append(format_html_exception(*self.main_traceback,
                **{"with_links": settings.DEV_MODE}))
        for index, tb in enumerate(self.threads_tracebacks.values()):
            parts.append(u"Thread %d:" % (index + 1))
            parts.append(format_html_exception(*tb, 
                **{"with_links": settings.DEV_MODE}))
        if settings.DEV_MODE:
            self.traceback_text.setHtml("".join(parts))
        else:
            self.traceback_text.setPlainText(u"\n".join(parts))

    def send_email(self):
        url = u"mailto:%s?subject=%s&body=%s\n\n%s" % (
            settings.BUG_REPORT_EMAIL, 
            settings.BUG_REPORT_EMAIL_SUBJECT,
            unicode(self.report_text.toPlainText()),
            unicode(self.traceback_text.toPlainText()))
        QDesktopServices.openUrl(QUrl(url))

    def accept(self):
        QDialog.accept(self)
        self.reset()

    def reject(self):
        QDialog.reject(self)
        QCoreApplication.exit(1)

    def debug(self):
        pyqtRemoveInputHook()
        pdb.pm()
        pyqtRestoreInputHook()
        self.accept()


__all__ = ["BugReportDialog"]
