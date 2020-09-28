# coding: utf-8

import sys
import cilogger.cilogger
log = cilogger.cilogger.ccilogger(__name__)


@cilogger.cilogger.ctrace
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

@cilogger.cilogger.ftrace
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
