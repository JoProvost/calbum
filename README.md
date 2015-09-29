[![Build Status](https://travis-ci.org/JoProvost/calbum.svg?branch=master)](https://travis-ci.org/JoProvost/calbum)
[![PyPI version](https://badge.fury.io/py/calbum.svg)](http://badge.fury.io/py/calbum)

calbum
======

__calbum__ is an unattended calendar-based photo organiser. It is meant to allow
easy management of pictures based on their location, date and calendar events
without the need of a database or a special browser to retrieve them.

How it works
------------

Pictures are moved from the _inbox_ folder to the _timeline_ and then linked to
an album based on the time period of an event found in the provided calendar.
Albums are named using the summary of the calendar event.  All characters that
are not allowed in a file name are discarted from the album name. Albums may
be deleted, pictures are kept in the timeline folder.

Usage
-----

    usage: calbum [-h] [--link-only] [--inbox path] [--timeline path]
                  [--album path] [--calendar url] [--date-format format]
                  [--save-events] [--time-zone tz]
    
    calbum is an unattended calendar-based photo organiser. It is meant to allow
    easy management of pictures based on their location, date and calendar events
    without the need of a database or a special browser to retrieve them.

    optional arguments:
      -h, --help            show this help message and exit
      --link-only           Keep files where they are in the inbox folder.
      --inbox path          The path of the inbox directory. (default: ./inbox)
      --timeline path       The path of the timeline directory. (default:
                            ./timeline)
      --album path          The path of the album directory. (default: ./album)
      --calendar url        The url of the album calendar. (ical)
      --date-format format  The format to use for timestamps.
      --save-events         Keep the calendar event in the album.
      --time-zone tz        Pictures timezone (default to local time).
