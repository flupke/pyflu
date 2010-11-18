import re


class Version(object):
    """
    Version numbers handling.

    Supports two types of versions numbering:
     * release versions, composed by a version number and an optional suffix.
       Examples in increasing order of versions:       
         1.0
         1.0a
         1.0beta
         1.0pre
         1.0pre2
         1.1
         1.1.2
         1.1.2_3
         1.1.2_10
     * snapshot versions, composed by a revision number and an optional branch
       specifier. The branch specifier is ignored in comparisons:
         r1
         r1234
         r1234-test (considered equal to the above)
         r12345-final

    Snapshots are _always_ considered superior to release numbers.
    """

    release_pattern = re.compile(r"^(?P<release>[0-9.]+)(?P<suffix>.*)$")
    snapshot_pattern = re.compile(r"^r(?P<revision>[0-9]+)-?(?P<branch>.*)$")

    def __init__(self, version_string):
        self.version_string = version_string
        match = self.release_pattern.match(version_string)        
        if match:
            self.is_release = True
            self.release_numbers = tuple(int(n) for n in 
                    match.group("release").split("."))
            self.release_suffix = match.group("suffix")
            if "_" in self.release_suffix:
                pre, rev = self.release_suffix.rsplit("_", 1)
                rev = int(rev)
            else:
                pre = self.release_suffix
                rev = 0
            self.release_suffix = (pre, rev)
        else:
            match = self.snapshot_pattern.match(version_string)
            if match:
                self.is_release = False
                self.snapshot_revision = int(match.group("revision"))
                self.snapshot_branch = match.group("branch")
            else:
                raise ValueError("unrecognized version pattern: %s" %
                        version_string)

    def __cmp__(self, other):
        if not isinstance(other, Version):
            if isinstance(other, str):
                other = Version(other)
            else:
                raise TypeError("invalid comparison between Version and %s" % 
                        other.__class__.__name__)
        if self.is_release:
            if other.is_release:
                # release-release comparison
                ret = cmp(self.release_numbers, other.release_numbers)
                if ret == 0:
                    # Version numbers are equal, compare suffix
                    ret = cmp(self.release_suffix, other.release_suffix)
            else:
                # release-snapshot comparison
                ret = -1
        else:
            if other.is_release:
                # snapshot-release comparison
                ret = 1
            else:
                # snapshot-snapshot comparison
                ret = cmp(self.snapshot_revision, other.snapshot_revision)
        return ret

    def __str__(self):
        return self.version_string

    def __hash__(self):
        if self.is_release:
            return hash((self.release_numbers, self.release_suffix))
        return hash(self.snapshot_revision)
