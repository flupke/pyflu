"""
An object oriented interface to getopt.
"""

import warnings
warnings.warn(DeprecationWarning("this module was written, then the author discovered "
        "optparse ..."))

import os.path
from getopt import gnu_getopt as getopt, GetoptError
import textwrap
import sys


class GetoptAppException(Exception): pass
class GetoptAppError(Exception): pass
class InvalidCommandLine(GetoptAppError): pass
class HelpPrinted(GetoptAppException): pass
class RequiredOptionMissing(GetoptAppError): pass


class Option(object):
    """Stores the description of a getopt option"""

    def __init__(self, long, short, takes_value, desc, required=False,
            default=None, multiple=False):
        self.short = short
        self.long = long
        self.takes_value = takes_value
        self.desc = desc
        self.required = required
        self.default = default
        self.multiple = multiple

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
            return "--%s -%s %s" % (self.long, self.short, value)
        return "--%s %s" % (self.long, value)


class OptionsList(object):
    """A list of Option objects"""

    def __init__(self, options, description, nb_args=None, 
            options_desc="[OPTIONS]", args_desc="[ARGS]"):
        self.nb_args = nb_args
        self.options_desc = options_desc
        if nb_args is None:
            self.args_desc = ""
        else:
            self.args_desc = args_desc
        self.options = [Option("help", None, False, "Print this help and exit")]
        self.by_short = {}
        self.by_long = {}
        self.description = description
        self.required_options = []
        self.defaults = {}
        for opt_desc in options:
            option = Option(*opt_desc)
            self.options.append(option)
            self.by_short[option.short] = option
            self.by_long[option.long] = option
            if option.required:
                self.required_options.append(option.long)
            if option.default is not None:
                self.defaults[option.long] = option.default
            elif option.multiple:
                self.defaults[option.long] = []

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
            raise InvalidCommandLine(str(e))
        # Print help if requested
        if ("--help", "") in options:
            print self.help(argv[0])
            sys.exit(0)
        # Verify number of arguments is correct
        if self.nb_args is not None and len(arguments) != self.nb_args:
            print "incorrect number of arguments, use --help to print help"
            sys.exit(1)
        # Transform the parsed options into a dictionnary mapping long option
        # names to values
        self.values = self.defaults.copy()
        for opt, value in options:
            # Strip the beginning - or --
            if opt.startswith("--"):
                key = opt[2:]
            else:
                key = self.by_short[opt[1:]].long
            if self.by_long[key].multiple:
                self.values[key].append(value)
            else:
                self.values[key] = value
        # Verify required options were passed
        for option_name in self.required_options:
            if option_name not in self.values:
                raise RequiredOptionMissing("required --%s option missing" %
                        option_name)
        return arguments

    def usage(self, executable):
        progname = os.path.split(executable)[1]
        return "Usage: %s %s %s" % (progname, self.options_desc,
                self.args_desc)

    def help(self, executable):
        options_text = []
        max_options_len = 0
        padding = 3
        # Get rendered options maximum text width
        for option in self.options:
            opt_text = " " * padding + str(option)
            options_text.append(opt_text)
            max_options_len = max(max_options_len, len(opt_text) + 1)
        # Render options description
        for i, option in enumerate(self.options):
            sep = " " * (max_options_len - len(options_text[i]))
            nl_sep = " " * max_options_len
            text = options_text[i] + sep + option.desc
            if option.default is not None:
                text += " [default: %s]" % option.default
            options_text[i] = "\n".join(textwrap.wrap(text, 
                subsequent_indent=nl_sep))
        return "%s\n%s\nOptions:\n%s\n" % (self.description, 
                self.usage(executable), "\n".join(options_text))

    def __getitem__(self, key):
        """
        Gets an option's value, looking up by its long form.
        
        If the option does not take a value, return True or False depending on
        the option presence.

        """
        option = self.by_long[key]
        if option.takes_value:
            return self.values.get(key, None)
        if self.values.has_key(key):
            return True
        return False

    def __setitem__(self, key, value):
        option = self.by_long[key]
        if option.takes_value:
            self.values[key] = value
        else:
            self.values[key] = bool(value)

    def __contains__(self, key):
        return self.values.has_key(key)
