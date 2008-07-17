"""
Object oriented interface to run commands
"""

class Command(object):
    """Stores a single GRASS command."""

    error_class = Exception

    def __init__(self, cmd, verbose=False, cwd=None, error_class=None):
        self.cmd = cmd
        self.verbose = verbose
        self.cwd = cwd
        self.error_class = error_class or Command.error_class
        
    def run(self, env=None, stop_on_errors=True):
        if self.verbose:
            print self.cmd
            stdout = stderr = None
        else:
            stdout = stderr = subprocess.PIPE
        process = subprocess.Popen([self.cmd], env=env, cwd=self.cwd, 
                shell=True, stdout=stdout, stderr=stderr)
        if process.wait():
            if stop_on_errors:
                raise self.error_class("Command '%s' returned %i" % 
                        (self.cmd, process.returncode))

    def __repr__(self):
        return "<Command: %s>" % self.cmd
