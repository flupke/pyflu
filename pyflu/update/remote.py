import urllib2
import re
from lxml import etree
from os.path import join, basename
from pyflu.update.version import Version
from urlparse import urljoin


def patches_chain(url, updates_pattern):
    """
    Retrieves the list of _consecutive_ patches on an HTML page.
    
    The links are parsed from the HTML page found at ``url``. Links not
    matching the regular expression ``updates_pattern`` are filtered.
    ``updates_pattern`` must define two groups named 'from' and 'to', isolating
    the versions numbers of the update.

    Returns a list of tuples containing 'from' and 'to' versions and the update
    file URL.

    A ValueError is raised if the chain of versions is not continuous. 
    """
    # Make sure the url has a trailing slash
    if not url.endswith("/"):
        url += "/"
    # Get links
    parser = etree.HTMLParser()
    doc = etree.parse(urllib2.urlopen(url), parser)
    updates_pattern = re.compile(updates_pattern)
    updates = []
    for link in doc.iterfind("//a"):
        href = urljoin(url, link.get("href"))
        filename = basename(href)
        match = updates_pattern.match(filename)
        if match:
            updates.append((
                Version(match.group("from")), 
                Version(match.group("to")), 
                href))
    # Verify updates chain continuity
    updates.sort(key=lambda x: x[0])
    last_version = None
    missing_updates = []
    for from_version, to_version, url in updates:
        if last_version is not None:
            if from_version != last_version:
                missing_updates.append((last_version, from_version))
        last_version = to_version
    if missing_updates:
        raise ValueError("missing udpates:\n%s" % 
                "\n".join(["%s => %s" % (f, t) for f, t in missing_updates]))
    return updates
