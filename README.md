CiLogger package
================

The cilogger module extends the python logging module to indent and color the logs and provides a log level of
type "TRACE". It also contains two decorators:

* A function decorator "@ftrace" that allows you to log function calls with its arguments
* A class decorator "@ctrace" that lets you log class method and property calls
  * \@ is used to show that it's a setter property call
  * \# is used to show that it's a getter property call

You can globaly disable ftrace and ctrace by adding these lines
```
cilogger.cilogger.ctrace_on = False
cilogger.cilogger.ftrace_on = False
```
Or you can disable ftrace and ctrace in decorator call with :
```
@cilogger.cilogger.ctrace(enable=False)
@cilogger.cilogger.ftrace(enable=False)
```

> :warning: **WARNING**
>
> :warning: Decorator call has changed !
>
> :warning: You must now put parenthesis in decorator's call
>
> Use :
>* ```@cilogger.cilogger.ctrace()``` instead of ```@cilogger.cilogger.ctrace```
>* ```@cilogger.cilogger.ftrace()``` instead of ```@cilogger.cilogger.ftrace```


Install :
---------

```
pip install git+https://github.com/christophe-marteau/python-cilogger#egg=cilogger
```

Use :
-----

```python
# coding: utf-8

import sys
import cilogger.cilogger
log = cilogger.cilogger.ccilogger(__name__)

# You can globaly disable ctrace and ftrace
# cilogger.cilogger.ctrace_on = False
# cilogger.cilogger.ftrace_on = False

## If you want only this decorator to be disable use :
# @cilogger.cilogger.ctrace(enable=False)
@cilogger.cilogger.ctrace()
class MyClass(object):
    def __init__(self):
        self.__log__.info('Init object')
        self._myattr = None

    def a_method(self):
        self.__log__.indent('DEBUG', 'Start a new indentation in a method')
        self.__log__.warning('Warning in a method')
        self.__log__.unindent('DEBUG', 'Ending indentation in a method')

    @property
    def myattr(self):
        self.__log__.error('Error in a getter')
        return self._myattr

    @myattr.setter
    def myattr(self, value):
        self._myattr = value
        self.__log__.critical('Critical in a setter')

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    @property
    def __log__(self):
        return cilogger.cilogger.ccilogger('{}.{}'.format(self.__class__.__module__, self.__class__.__name__))

## If you want only this decorator to be disable use :
# @cilogger.cilogger.ftrace(enable=False)
@cilogger.cilogger.ftrace()
def main():
    log.debug('My debug message in an indented function')
    mc = MyClass()
    mc.myattr = 'plic'
    mc.a_method()
    x = mc.myattr
    x = '{}'.format(x)
    mc.myattr = x


if __name__ == '__main__':
    cilogger.cilogger.rootlogger.setLevel('TRACE')
    sys.exit(main())
```

    Example output with colorized and indented logs:

![Example output with colorized and indented logs](doc/source/example.png)


    Copyright (C) 2019  Christophe Marteau

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
