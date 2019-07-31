CiLogger package
================

The cilogger module extends the python logging module to indent and color the logs and provides a log level of
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