import urllib2
import re
from lxml import etree
from os.path import join, basename
from pyflu.update.version import Version


def updates_urls(url, updates_pattern):
    """
    Retrieves the update links from an HTML page.
    
    The links are parsed from the HTML page found at ``url``. Links not
    matching the regular expression ``updates_pattern`` are filtered.
    ``updates_pattern`` must define a group named 'version'.

    Returns a list of tuples containing a Version object and the full URL for
    each update link, sorted by version, from the more recent to the oldest.
    """
    parser = etree.HTMLParser()
    doc = etree.parse(urllib2.urlopen(url), parser)
    updates_pattern = re.compile(updates_pattern)
    updates = []
    for link in doc.iterfind("//a"):
        href = join(url, link.get("href"))
        filename = basename(href)
        match = updates_pattern.match(filename)
        if match:
            updates.append(Version(match.group("version")), href)
    updates.sort(key=lambda x: x[0], reverse=True)
    return updates
