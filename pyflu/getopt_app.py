"""
An object oriented interface to getopt.

Here is an example for a program that wants exactly one argument and can take
thre options, of which two don't take a value :

>>> options = OptionsList((
...         ("profile", "p", False, "Do a profiling run"),
...         ("debug", "d", False, "Print debug information"),
...         ("name", None, True, "Specify a name"),
...     ), 
...     nb_args=1, 
... )
>>> arguments = options.parse(["-p", "--name", "john", "woo"])
>>> arguments[0]
'woo'
>>> options["p"]
True
>>> options["profile"]
True
>>> options["d"]
False
>>> options["name"]
'john'
>>> arguments = options.parse(["-p", "--name", "john", "woo"])

"""

import sys
import os.path
from getopt import gnu_getopt as getopt, GetoptError


class Option(object):
    """Stores the description of a getopt option"""

    def __init__(self, long, short, takes_value, desc):
        self.short = short
        self.long = long
        self.takes_value = takes_value
        self.desc = desc

    def short_getopt(self):
        if not self.short:
            return ""
        opt = self.short
        if self.takes_value:
            opt += ":"
        return opt

    def long_getopt(self):
        opt = self.long
        if self.takes_value:
            opt += "="
        return opt

    def __str__(self):
        if self.takes_value:
            value = "VALUE"
        else:
            value = ""
        if self.short:
            return "\t--%s -%s %s\n\t\t%s" % (self.long, self.short, value,
                    self.desc)
        return "\t--%s %s\n\t\t%s" % (self.long, value, self.desc)


class OptionsList(object):
    """A list of Option objects"""

    def __init__(self, values, nb_args=None, options_desc="[OPTIONS]",
            args_desc="[ARGS]"):
        self.nb_args = nb_args
        self.options_desc = options_desc
        self.args_desc = args_desc
        self.options = [Option("help", None, False, "print help")]
        self.by_short = {}
        self.by_long = {}
        for opt_desc in values:
            option = Option(*opt_desc)
            self.options.append(option)
            self.by_short[option.short] = option
            self.by_long[option.long] = option

    def parse(self, argv):
        # Make the getopt arguments
        short_opts = ""
        long_opts = []
        for option in self.options:
            short_opts += option.short_getopt()
            long_opts.append(option.long_getopt())
        # Parse commandline using getopt
        try: 
            options, arguments = getopt(argv[1:], short_opts, long_opts)
        except GetoptError, e:
            print e
            print self.usage(argv[0])
            sys.exit(1)
        # Print help if requested
        if ("--help", "") in options:
            print self.help(argv[0])
            sys.exit(0)
        # Verify number of arguments is correct
        if self.nb_args is not None and len(arguments) != self.nb_args:
            print self.usage(argv[0])
            sys.exit(1)
        # Transform the parsed options into a dictionnary mapping long option
        # names to values
        self.values = {}
        for opt, value in options:
            # Strip the beginning - or --
            if opt.startswith("--"):
                self.values[opt[2:]] = value
            else:
                self.values[self.by_short[opt[1:]].long] = value
        return arguments

    def usage(self, executable):
        progname = os.path.split(executable)[1]
        return "Usage: %s %s %s" % (progname, self.options_desc,
                self.args_desc)

    def help(self, executable):
        return "%s\n%s" % (self.usage(executable), 
                "\n".join([str(x) for x in self.options]))

    def __getitem__(self, key):
        """
        Gets an option's value, looking up by its long form.
        
        If the option does not take a value, return True or False depending on
        the option presence.

        """
        option = self.by_long[key]
        if option.takes_value:
            return self.values[key]
        if self.values.has_key(key):
            return True
        return False

