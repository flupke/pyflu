"""
Global settings for the bug report dialog.
"""

# If True, display the 'Debug' button and make the tracebacks clickable
DEV_MODE = True

# Path to the external text editor launched when a traceback is clicked
EXTERNAL_EDITOR = "/usr/bin/gvim --remote-silent %f +%n"

# Email to which bug reports are sent
BUG_REPORT_EMAIL = None
BUG_REPORT_EMAIL_SUBJECT = "Bug report"
