from docutils.core import publish_parts
from docutils.parsers import rst


def rst2html(text):
    """
    Convert reStructuredText *text* to a piece of HTML, e.g.:

    >>> rst2html("I'm a *reST* string")
    u"<p>I'm a <em>reST</em> string</p>\\n"
    """
    inliner = rst.states.Inliner()
    parser = rst.Parser(inliner=inliner)
    parts = publish_parts(text, writer_name="html", parser=parser,
            settings_overrides={
                "halt_level": 6, 
                "file_insertion_enabled": 0, 
                "raw_enabled": 0
            })
    return parts["body"]
