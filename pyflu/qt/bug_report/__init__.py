import sys
from pyflu.qt.bug_report.dialog import BugReportDialog
from pyflu.qt.bug_report.tb import install_ext_editor_url_handler
from pyflu.qt.bug_report import settings


bug_report_dlg = None


def excepthook(type, value, tb):
    bug_report_dlg.show()
    bug_report_dlg.add_tb(type, value, tb)


def install(parent=None, bug_report_email=None):
    """
    Install a custom exception hook that displays the bug report dialog on
    errors.

    This should be called early, before other windows, to catch initialization
    errors (for example just after the QApplication has been created).
    """
    global bug_report_dlg
    settings.BUG_REPORT_EMAIL = bug_report_email
    bug_report_dlg = BugReportDialog(parent)
    sys.excepthook = excepthook
    install_ext_editor_url_handler()
