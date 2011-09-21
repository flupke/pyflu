import sys
import thread
from PyQt4.QtCore import QObject, pyqtSignal, Qt
from pyflu.qt.bug_report.dialog import BugReportDialog
from pyflu.qt.bug_report.tb import install_ext_editor_url_handler
from pyflu.qt.bug_report import settings


bug_report_dlg = None
tb_sender = None


class TracebackSender(QObject):
    """
    An intermediary to send tracebacks from other threads.
    """

    traceback_sent = pyqtSignal(object, object, object, object)


def excepthook(type, value, tb):
    thread_id = thread.get_ident()
    tb_sender.traceback_sent.emit(thread_id, type, value, tb)


def install(parent=None, bug_report_email=None):
    """
    Install a custom exception hook that displays the bug report dialog on
    errors.

    This should be called early, before other windows, to catch initialization
    errors (for example just after the QApplication has been created).
    """
    global bug_report_dlg, tb_sender
    settings.BUG_REPORT_EMAIL = bug_report_email
    bug_report_dlg = BugReportDialog(parent)
    tb_sender = TracebackSender()
    tb_sender.traceback_sent.connect(bug_report_dlg.add_tb, 
            Qt.QueuedConnection)
    sys.excepthook = excepthook
    install_ext_editor_url_handler()
