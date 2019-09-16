# coding: utf-8
""" The cilogger module extends the python logging module to indent and color the logs and provides a log level of
type "TRACE". It also contains two decorators:

* A function decorator "@ftrace" that allows you to draw function calls with its arguments
* A class decorator "@ctrace" that lets you plot method and property calls

Example :

.. literalinclude:: example.py
    :language: python

.. figure:: example.png
    :align: center
    :alt: Sample output
    :figclass: align-center

    Example output with colorized and indented logs

.. note:: Copyright (C) 2019  Christophe Marteau

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>
"""

import logging as log
import typing
import colors
import re


def finspect(f, fargs) -> dict:
    """ This function retrieves real module name and function name to be used in a function wrapper

    It also checks for properties and class methods names

    :param function f: A wrapped function
    :param tuple fargs: Function's args
    :return: A dict with module name and function name. Default to {'module': f.__module__, 'name': f.__name__}
    """
    fname = f.__name__
    ftype = None

    if hasattr(f, '__self__'):
        a = getattr(f, '__self__')
        if f.__name__ == '__get__' and hasattr(a, 'fget'):
            # Found a getter property
            p = getattr(a, 'fget')
            fname = getattr(p, '__name__')
            ftype = 'getter'
        if f.__name__ == '__set__' and hasattr(a, 'fset'):
            # Found a getter propertylocals().keys()
            p = getattr(a, 'fset')
            fname = getattr(p, '__name__')
            ftype = 'setter'
        if f.__name__ == '__delattr__' and hasattr(a, 'fdel'):
            # Found a getter property
            p = getattr(a, 'fdel')
            fname = getattr(p, '__name__')
            ftype = 'deleter'

    if len(fargs) > 0:
        instance = fargs[0]
        if isinstance(instance, object) and fname in dir(instance):
            fmodule = '.'.join([instance.__class__.__module__, instance.__class__.__name__])
        else:
            fmodule = f.__module__
    else:
        fmodule = f.__module__

    return {'module': fmodule, 'name': fname, 'type': ftype}


def ftrace(fct: typing.Callable) -> typing.Callable:
    """Decorator for tracing functions
    This decorator decorate a function by inserting a trace log with function arguments before and after

    * When entering a function it logs as a trace: **fct( \\*[<args list>], \\*\\*{<kwargs list>})**
    * When leaving a function it logs as a trace: **fct( \\*[<args list>], \\*\\*{<kwargs list>}) = <value>**

    :param function fct: The function to decorate
    :return: A wrapper to a function
    """
    import inspect

    def ftraced(*args, **kwargs):
        cargs = [a for a in args]
        signature = inspect.signature(fct)
        dargs = [v.default for k, v in signature.parameters.items() if v.default is not inspect.Parameter.empty]
        fi = finspect(fct, args)
        locallogger = ccilogger(fi['module'])
        if fi['type'] == 'setter':
            aargs = cargs + dargs
            locallogger.log(locallogger.TRACE, '( {} ) => set( {} )'.format(aargs[0], aargs[1]),
                            extra={'realFunctionName': fi['name'], 'prefix': '',
                                   'padding_default_char': ' ',
                                   'padding_default_enclosure_char': '@'})
        elif fi['type'] is None:
            locallogger.indent('TRACE', '( *{}, **{} )'.format(cargs + dargs, kwargs),
                               extra={'realFunctionName': fi['name'], 'prefix': ''})
        x = fct(*args, **kwargs)
        if fi['type'] == 'getter':
            aargs = cargs + dargs
            locallogger.log(locallogger.TRACE, '( {} ) <= get( {} )'.format(aargs[0], x),
                            extra={'realFunctionName': fi['name'], 'prefix': '',
                                   'padding_default_char': ' ',
                                   'padding_default_enclosure_char': '#'})
        elif fi['type'] is None:
            locallogger.unindent('TRACE', '( *{}, **{} ) = {}'.format(cargs + dargs, kwargs, x),
                                 extra={'realFunctionName': fi['name'], 'prefix': ''})
        return x
    return ftraced


def ctrace(cls: object):
    """Decorator for tracing all methods and properties in a class
    This decorator add a ftrace decorator on each method and property o the class

    :param class cls: The class to decorate
    :return: A class with all methods and properties wrapped by a ftrace decorator
    """
    import types
    for method in dir(cls):
        m = getattr(cls, method)
        if isinstance(m, types.FunctionType) and m.__name__ == '__init__':
            setattr(cls, method, ftrace(m))
        if isinstance(m, types.FunctionType) \
                and not m.__name__ == 'ftraced' \
                and not m.__name__.startswith('__') \
                and not m.__name__.endswith('__'):
            setattr(cls, method, ftrace(m))
        if isinstance(m, property) and \
                ((m.fget is not None and m.fget.__name__ not in ['log', '_log', '__log__', 'ftraced']) or
                 (m.fset is not None and m.fset.__name__ not in ['log', '_log', '__log__', 'ftraced']) or
                 (m.fdel is not None and m.fdel.__name__ not in ['log', '_log', '__log__', 'ftraced'])):
            setattr(cls, method, property(ftrace(m.__get__), ftrace(m.__set__), ftrace(m.__delattr__)))
    return cls


class CiFormatter(log.Formatter):
    """Custom logging Formatter for colorizing all record that are bounded with a color or level tag:

     * <color ...>{record}</> for static user define color
     * <level>{record}</> for a level dependent color

    The color's properties inside a color tag are specified with fg=... bg=... style=... as in the colors
    module from ansicolors
    """
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)

    def _get_color(self: object, scolor: str, c: dict):
        """This function inspect recursively the string searching 'fg', 'bg' and 'style' tags
        and assign the founded color to the color dict

        :param str scolor: The color string to inspect
        :param dict c: The color dict {'fg': <fg color>, 'bg': <bg color>, 'style': <style>}
        :return: The color dict with founded colors
        """
        cregex = re.compile(r'(fg|bg|style)=(\S+)')
        m = cregex.search(scolor)
        if m:
            tag = m.group(1)
            ctag = m.group(2)
            c[tag] = ctag
            return self._get_color(cregex.sub('', scolor, 1), c)
        else:
            return c

    def _colorize(self, s: str, record: object):
        """ Colorize a string with a static color or a level dependent color. Colors are set in the format logger
        string and parsed recursively by this function

        :param str s: A string containing the message to colorize.
        :param object record: A record object containing level's colors
        :return: A colorized string
        """
        sregex = re.compile(r'<(color|level)\s*([^>]*)>(.+?)</>')
        m = sregex.search(s)
        if m:
            tag = m.group(1)
            scolor = m.group(2)
            w = m.group(3)
            c = {'fg': None, 'bg': None, 'style': None}
            if tag == 'level':
                if record.levelname in record.clevel:
                    c = record.clevel[record.levelname]
            else:
                c = self._get_color(scolor, c)
            wcolor = colors.color(w, fg=c['fg'], bg=c['bg'], style=c['style'])
            return self._colorize(sregex.sub(wcolor, s, 1), record)
        else:
            return s

    def format(self, record: object):
        """ The logging Formatter format function and after we apply our colorize method

        :param object record: Logging's record
        :return: The logging message
        """
        s = super().format(record)
        s = self._colorize(s, record)
        return s


class CiLogger(log.getLoggerClass()):
    """ This class provides an extension to the logging module and adds logs indentation and colorization

    """

    #: Current indent count
    indent_count = 1
    #: Indent step
    indent_step = 1
    #: Indent padding enclosure when not starting or ending an indent block
    padding_default_enclosure_char = '  '
    #: Indent padding char when not starting or ending an indent block
    padding_default_char = ' '
    #: Indent padding enclosure when starting a new indent block
    padding_start_enclosure_char = '>'
    #: Indent padding enclosure when ending an indented block
    padding_end_enclosure_char = '<'
    #: Indent padding char when starting a new indented block
    padding_start_char = '-'
    #: Indent padding char when ending an indented block
    padding_end_char = '-'
    #: Default record prefix which can be use in a formatter
    message_default_prefix = ': '
    levelcolors = {'NOTSET': {'fg': 'green', 'bg': None, 'style': None},
                   'TRACE': {'fg': 'turquoise', 'bg': None, 'style': 'bold'},
                   'DEBUG': {'fg': 'blue', 'bg': None, 'style': 'bold'},
                   'INFO': {'fg': None, 'bg': None, 'style': 'bold'},
                   'WARNING': {'fg': 'orange', 'bg': None, 'style': 'bold'},
                   'ERROR': {'fg': 'red', 'bg': None, 'style': 'bold'},
                   'CRITICAL': {'fg': 'brown', 'bg': 'tomato', 'style': 'bold'}}
    """
    Default level colors :
    
    +----------+------------------+------------------+-------+
    | Level    | Foreground color | Background color | Style |
    +==========+==================+==================+=======+
    | NOTSET   | green            | None             | None  |
    +----------+------------------+------------------+-------+
    | TRACE    | turquoise        | None             | bold  |
    +----------+------------------+------------------+-------+
    | DEBUG    | blue             | None             | bold  |
    +----------+------------------+------------------+-------+
    | INFO     | None             | None             | bold  |
    +----------+------------------+------------------+-------+
    | WARNING  | orange           | None             | bold  |
    +----------+------------------+------------------+-------+
    | ERROR    | red              | None             | bold  |
    +----------+------------------+------------------+-------+
    | CRITICAL | brown            | tomato           | bold  |
    +----------+------------------+------------------+-------+
    """

    def __init__(self: object, name: str, level: int = log.NOTSET):
        super().__init__(name=name, level=level)
        self.NOTSET = log.NOTSET
        self.TRACE = 5
        self.DEBUG = log.DEBUG
        self.INFO = log.INFO
        self.WARNING = log.WARNING
        self.ERROR = log.ERROR
        self.FATAL = log.FATAL
        self.CRITICAL = log.CRITICAL
        log.addLevelName(self.TRACE, 'TRACE')
        self.addFilter(self._internal_filter)

    def _lvl2int(self: object, lvl: str) -> int:
        """ Convert a string level to int level

        :param str lvl: A string level
        :return: Int level
        """
        if isinstance(lvl, str):
            return getattr(self, lvl)
        else:
            return int(lvl)

    @staticmethod
    def _update_extra(kwargs: dict, attribut: str, value: any):
        """ Update extra dict in kwargs if exists with {attribut: value}

        :param dict kwargs: A kwargs dict
        :param str attribut:
        :param any value:
        :return: A kwargs dict updated with {attribut: value}
        """
        if 'extra' in kwargs:
            kwargs['extra'].update({attribut: value})
        else:
            kwargs.update({'extra': {attribut: value}})
        return kwargs

    def indent(self: object, level: typing.Union[int, str], msg: str, *args, **kwargs):
        """Logs a message and starts a new indent block. The arguments are interpreted as for the
        `log() <https://docs.python.org/3/library/logging.html#logging.Logger.log>`_ function from the
        `logging module <https://docs.python.org/3/library/logging.html>`_
        """
        type(self).indent_count += self.indent_step
        self._update_extra(kwargs, 'indent', 'start')
        intlevel = self._lvl2int(level)
        if self.isEnabledFor(intlevel):
            self._log(intlevel, msg, args, **kwargs)

    def unindent(self: object, level: typing.Union[int, str], msg: str, *args, **kwargs):
        """Logs a message and ends an indented block. The arguments are interpreted as for the
        `log() <https://docs.python.org/3/library/logging.html#logging.Logger.log>`_ function from the
        `logging module <https://docs.python.org/3/library/logging.html>`_
        """
        self._update_extra(kwargs, 'indent', 'end')
        intlevel = self._lvl2int(level)
        if self.isEnabledFor(intlevel):
            self._log(intlevel, msg, args, **kwargs)
        type(self).indent_count -= self.indent_step

    def trace(self: object, msg: str, *args, **kwargs):
        """ Logs a message with level TRACE on this logger. The arguments are interpreted as for the
        `debug() <https://docs.python.org/3/library/logging.html#logging.Logger.debug>`_ function from the
        `logging module <https://docs.python.org/3/library/logging.html>`_
        """
        if self.isEnabledFor(self.TRACE):
            self._log(self.TRACE, msg, args, **kwargs)

    def _internal_filter(self: object, record: object) -> bool:
        """ Internal default logging filter use to manage indentation

        :param record: A logging recod object
        :return: True
        """
        record.clevel = self.levelcolors

        if not hasattr(record, 'indent'):
            record.indent = 'default'
        if not hasattr(record, 'padding_default_char'):
            record.padding_default_char = self.padding_default_char
        if not hasattr(record, 'padding_default_enclosure_char'):
            record.padding_default_enclosure_char = self.padding_default_enclosure_char
        if not hasattr(record, 'prefix'):
            record.prefix = self.message_default_prefix
        if not hasattr(record, 'realFunctionName'):
            record.realFunctionName = record.funcName

        record.padding = '{:{}>{}}'.format(record.padding_default_enclosure_char,
                                           record.padding_default_char, self.indent_count)

        if record.indent == 'start':
            record.padding = '{:{}>{}}'.format(self.padding_start_enclosure_char,
                                               self.padding_start_char, self.indent_count)
        elif record.indent == 'end':
            record.padding = '{:{}<{}}'.format(self.padding_end_enclosure_char,
                                               self.padding_end_char, self.indent_count)

        return True


log.setLoggerClass(CiLogger)


def _rcilogger():
    """ Get a a root logger. This function should not be call outside this module

    :return: A root CiLogger with default message formatter
    """
    log.setLoggerClass(CiLogger)
    handler = log.StreamHandler()
    ciformatter = CiFormatter('<color fg=cyan>{asctime:12s}</> '
                              '<level>{levelname: >8s}</> '
                              '<color fg=green>{name: >35s}:</> '
                              '<color fg=grey bg=#414141>{padding}</>'
                              '<color fg=magenta>{realFunctionName}</>'
                              '{prefix}<level>{message}</>',
                              style='{')
    handler.setFormatter(ciformatter)
    rlogger = log.getLogger('root')
    rlogger.addHandler(handler)
    return rlogger


rootlogger = _rcilogger()
""" 
A root Logger that can be use in main script to set default level. 

Example :

.. code-block:: python
    
    import cilogger.cilogger
    log = cilogger.cilogger.ccilogger(__name__)

    def main():
        log.error("my error message")

    if __name__ == '__main__':
        cilogger.cilogger.rootlogger.setLevel('INFO')
        sys.exit(main())   
"""


def ccilogger(name):
    """ Get a child logger in a module

    :param name: Child logger name
    :return: A child CiLogger
    """
    return rootlogger.getChild(name)
