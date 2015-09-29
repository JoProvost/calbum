# Copyright 2015 Jonathan Provost.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from datetime import datetime, date, timedelta

from hamcrest import assert_that, is_
from icalendar import Event
import pytz

from calbum.sources.calendar import CalendarTimePeriod


class TestEventTimePeriod(unittest.TestCase):

    def test_timestamp_in_simple_event(self):
        etp = CalendarTimePeriod(Event.from_ical("""BEGIN:VEVENT
DTSTART:20151010T100000Z
DTEND:20151010T120000Z
CREATED:20151010T100000Z
UID:123456
END:VEVENT"""))

        assert_that(etp.start(), is_(datetime(2015, 10, 10, 10, tzinfo=pytz.utc)))
        assert_that(etp.duration(), is_(timedelta(hours=2)))

        assert_that(datetime(2015, 10, 10, 11, tzinfo=pytz.utc) in etp, is_(True))

        assert_that(datetime(2015, 10, 10, 9, tzinfo=pytz.utc) in etp, is_(False))

        assert_that(datetime(2015, 10, 10, 13, tzinfo=pytz.utc) in etp, is_(False))

    def test_timestamp_in_simple_recursive_event(self):
        etp = CalendarTimePeriod(Event.from_ical("""BEGIN:VEVENT
DTSTART:20151010T100000Z
DTEND:20151010T120000Z
CREATED:20151010T100000Z
RRULE:FREQ=DAILY;COUNT=2
UID:123456
END:VEVENT"""))

        assert_that(etp.start(), is_(datetime(2015, 10, 10, 10, tzinfo=pytz.utc)))
        assert_that(etp.duration(), is_(timedelta(hours=2)))

        assert_that(datetime(2015, 10, 10, 11, tzinfo=pytz.utc) in etp, is_(True))
        assert_that(datetime(2015, 10, 10, 9, tzinfo=pytz.utc) in etp, is_(False))
        assert_that(datetime(2015, 10, 10, 13, tzinfo=pytz.utc) in etp, is_(False))


        assert_that(datetime(2015, 10, 11, 11, tzinfo=pytz.utc) in etp, is_(True))
        assert_that(datetime(2015, 10, 11, 9, tzinfo=pytz.utc) in etp, is_(False))
        assert_that(datetime(2015, 10, 11, 13, tzinfo=pytz.utc) in etp, is_(False))

        assert_that(datetime(2015, 10, 12, 11, tzinfo=pytz.utc) in etp, is_(False))

    def test_timestamp_in_recursive_event_with_exceptions(self):
        etp = CalendarTimePeriod(Event.from_ical("""BEGIN:VEVENT
DTSTART:20151010T100000Z
DTEND:20151010T120000Z
CREATED:20151010T100000Z
RRULE:FREQ=DAILY;COUNT=5
EXDATE:20151011T100000Z,20151012T100000Z
EXDATE:20151013T100000Z
UID:123456
END:VEVENT"""))

        assert_that(etp.start(), is_(datetime(2015, 10, 10, 10, tzinfo=pytz.utc)))
        assert_that(etp.duration(), is_(timedelta(hours=2)))

        assert_that(datetime(2015, 10, 10, 11, tzinfo=pytz.utc) in etp, is_(True))
        assert_that(datetime(2015, 10, 10, 9, tzinfo=pytz.utc) in etp, is_(False))
        assert_that(datetime(2015, 10, 10, 13, tzinfo=pytz.utc) in etp, is_(False))

        assert_that(datetime(2015, 10, 11, 11, tzinfo=pytz.utc) in etp, is_(False))
        assert_that(datetime(2015, 10, 12, 11, tzinfo=pytz.utc) in etp, is_(False))
        assert_that(datetime(2015, 10, 13, 11, tzinfo=pytz.utc) in etp, is_(False))

        assert_that(datetime(2015, 10, 14, 11, tzinfo=pytz.utc) in etp, is_(True))

        assert_that(datetime(2015, 10, 15, 11, tzinfo=pytz.utc) in etp, is_(False))

    def test_timestamp_in_timeless_event(self):
        etp = CalendarTimePeriod(Event.from_ical("""BEGIN:VEVENT
DTSTART;VALUE=DATE:20151113
DTEND;VALUE=DATE:20151114
DTSTAMP:20150925T034508Z
UID:9E783D57-BF34-47B0-86D8-FE6FD83B05A2
SEQUENCE:0
CREATED:20150922T191411Z
LAST-MODIFIED:20150922T191823Z
END:VEVENT"""))

        assert_that(etp.start(), is_(date(2015, 11, 13)))
        assert_that(etp.duration(), is_(timedelta(days=1)))

        assert_that(datetime(2015, 11, 12, 12, tzinfo=pytz.utc) in etp, is_(False))
        assert_that(datetime(2015, 11, 13, 12, tzinfo=pytz.utc) in etp, is_(True))
        assert_that(datetime(2015, 11, 14, 9, tzinfo=pytz.utc) in etp, is_(False))

    def test_timestamp_in_byday_event(self):
        etp = CalendarTimePeriod(Event.from_ical("""BEGIN:VEVENT
DTSTART;TZID=America/Toronto:20150602T183000
DTEND;TZID=America/Toronto:20150602T193000
DTSTAMP:20150925T035639Z
SEQUENCE:0
EXDATE;TZID=America/Toronto:20150827T183000
CREATED:20150519T235325Z
LAST-MODIFIED:20150706T153006Z
RRULE:FREQ=WEEKLY;UNTIL=20150827T223000Z;BYDAY=TU,TH;WKST=SU
END:VEVENT"""))

        assert_that(etp.start(), is_(datetime(2015, 06, 02, 18, 30, tzinfo=pytz.timezone('Etc/GMT+4'))))
        assert_that(etp.duration(), is_(timedelta(hours=1)))

        assert_that(datetime(2015, 11, 12, 12, tzinfo=pytz.timezone('Etc/GMT+4')) in etp, is_(False))

    def test_timestamp_in_yearly_event(self):
        etp = CalendarTimePeriod(Event.from_ical("""BEGIN:VEVENT
DTSTART;VALUE=DATE:20120702
DTEND;VALUE=DATE:20120703
DTSTAMP:20150925T043431Z
SEQUENCE:2
CREATED:20110922T001534Z
LAST-MODIFIED:20150706T153006Z
RRULE:FREQ=YEARLY
END:VEVENT"""))

        assert_that(etp.start(), is_(date(2012, 07, 02)))
        assert_that(etp.duration(), is_(timedelta(days=1)))

        assert_that(datetime(2012, 07, 02, 12) in etp, is_(True))

    def test_timestamp_in_event_without_an_end(self):
        etp = CalendarTimePeriod(Event.from_ical("""BEGIN:VEVENT
DTSTART:20130921T230000Z
DTSTAMP:20150925T051339Z
SEQUENCE:1
CREATED:20130903T183447Z
LAST-MODIFIED:20130916T165029Z
END:VEVENT"""))

        assert_that(etp.start(), is_(datetime(2013, 9, 21, 23, tzinfo=pytz.utc)))
        assert_that(datetime(2013, 9, 21, 23, tzinfo=pytz.utc) in etp, is_(False))
