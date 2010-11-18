import urllib2
import re
from lxml import etree
from os.path import join, basename
from urlparse import urljoin
from pyflu.update.version import Version
from pyflu.odict import odict


def find_patches_groups(url, updates_pattern):
    """
    Retrieves groups of _consecutive_ patches in an HTML page.
    
    The links are parsed from the HTML page found at *url*. Links not
    matching the regular expression *updates_pattern* are filtered.
    *updates_pattern* must define two groups named 'from' and 'to', isolating
    the version numbers of the update.

    Returns an :class:`~pyflu.odict.odict` object, containing lists of update
    chains (updates that can be applied successively to update from a version
    to another), indexed by the first :class:`~pyflu.update.version.Version` 
    object of the chain.
    """
    # Get links from the HTML update page
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
    # Create version groups
    updates.sort(key=lambda x: x[0])
    last_version = None
    groups = odict()
    current_group = []
    for from_version, to_version, url in updates:
        if last_version is not None:
            if from_version != last_version:
                groups[current_group[0][0]] = current_group
                current_group = []
        last_version = to_version
        current_group.append((from_version, to_version, url))
    if current_group:
        groups[current_group[0][0]] = current_group
    return groups
