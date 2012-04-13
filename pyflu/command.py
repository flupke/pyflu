"""
Object oriented interface to run commands
"""


import subprocess
import os
import shlex


class Command(object):
    """Stores a single shell command."""

    error_class = Exception

    def __init__(self, cmd, cwd=None, error_class=None):
        self.cmd = cmd
        self.cwd = cwd
        self.error_class = error_class or Command.error_class
        
    def run(self, env=None, stop_on_errors=True):
        stdout = stderr = subprocess.PIPE
        if subprocess.call([self.cmd], env=env, cwd=self.cwd, 
                shell=True, stdout=stdout, stderr=stderr) and stop_on_errors:
            raise self.error_class("error executing '%s'" % self.cmd)

    def __repr__(self):
        return "<Command: %s>" % self.cmd

    def __str__(self):
        return self.cmd


def run_script(lines, stop_on_errors=True, pipe_output=False, echo=False,
        cwd=None, null_output=False):
    """Run subprocess commands from a string or a list of strings"""
    if not isinstance(lines, (list, dict)):
        lines = [lines]
    output_data = []
    for line in lines:
        if pipe_output:
            stderr = stdout = subprocess.PIPE
        elif null_output:
            stderr = stdout = open(os.devnull, "w")
        else:
            stderr = stdout = None
        if echo:
            print line
        proc = subprocess.Popen(shlex.split(line), stderr=stderr, stdout=stdout,
                cwd=cwd)
        if pipe_output:
            output_data.append(proc.communicate())
        ret = proc.wait()
        if stop_on_errors and ret != 0:
            raise Exception("error running '%s', return value %s" % (line, ret))
    return output_data
