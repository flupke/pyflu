"""
Utilities to display tracebacks nicely.
"""

import os
import traceback
import re
from StringIO import StringIO
from PyQt4.QtCore import QObject, pyqtSlot, QUrl
from PyQt4.QtGui import QDesktopServices
from pyflu.qt.bug_report import settings
from xml.sax.saxutils import escape


files_re = re.compile(r'^( *)File "(.*)", line ([0-9]+), (.*)$')
exc_re = re.compile(r'^([a-zA-Z][a-zA-Z0-9.]+:) (.*)$')
ext_edit_protocol = "bugreporteditor"


def format_html_exception(type, value, tb, with_links=True):
    """
    Render a traceback to a HTML string.

    If *with_links* is True, replace the file references in the traceback with
    clickable links launching an external editor.
    """
    out = StringIO()
    traceback.print_exception(type, value, tb, file=out)
    out.seek(0)
    return htmlify_traceback(out, with_links=with_links)


def htmlify_traceback(tb, with_links=True):
    """
    Convert a standard Python traceback to HTML.
    """
    if isinstance(tb, basestring):
        tb = StringIO(tb)
    html_out = []
    got_last_line = False
    multi_line_error = False
    for num, line in enumerate(tb):
        cleaned_line = escape(line.strip())
        if num:
            if line.startswith("  File"):
                # File line
                if with_links:
                    html_out.append(files_re.sub(
                        r'<li>File "<a href="%s:/\2+\3">\2</a>", line \3, \4' %
                        ext_edit_protocol, cleaned_line))
                else:
                    html_out.append(files_re.sub(r'<li>File "\2", line \3, \4' %
                        ext_edit_protocol, cleaned_line))
            elif line.startswith(" "):
                # Code line
                html_out.append("<br/><code>%s</code></li>" % cleaned_line)
            else:
                # Error line (last line)
                if not got_last_line:
                    html_out.append(exc_re.sub(r"</ul><strong>\1</strong> \2",
                        cleaned_line))
                    got_last_line = True
                    on_first_extra_line = True
                else:
                    # We have a multi line error message
                    if on_first_extra_line:
                        html_out.append("<blockquote>%s" % cleaned_line)
                        on_first_extra_line = False
                        multi_line_error = True
                    else:
                        html_out.append("<br/>%s" % cleaned_line)
        else:
            # First line is the traceback header
            html_out.append("<p>%s<ul>" % line.strip())
    if multi_line_error:
        html_out.append("</blockquote>")
    html_out.append("</p>")
    return "".join(html_out)


def install_ext_editor_url_handler():
    """
    Install the URL handler that opens the external editor from traceback
    links.
    """
    QDesktopServices.setUrlHandler(ext_edit_protocol,
            dummy_receiver.open_external_editor)
    

class DummyUrlHandler(QObject):
    """
    Used by :func:`install_ext_editor_url_handler` that needs a pyqtSignature
    decorated slot to work properly.
    """

    @pyqtSlot(QUrl) 
    def open_external_editor(self, url):
        """
        External editor URL handler.
        """
        path, line = unicode(url.toString())[len("%s:/" % ext_edit_protocol):] \
                .split("+")
        editor = settings.EXTERNAL_EDITOR
        editor = editor.replace("%f", path).replace("%n", line)
        os.system(editor)


dummy_receiver = DummyUrlHandler()
