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
from datetime import datetime

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

        assert_that(etp.begin(), is_(datetime(2015, 10, 10, 10, tzinfo=pytz.utc)))
        assert_that(etp.end(), is_(datetime(2015, 10, 10, 12, tzinfo=pytz.utc)))

        assert_that(datetime(2015, 10, 10, 11) in etp, is_(True))

        assert_that(datetime(2015, 10, 10, 9) in etp, is_(False))

        assert_that(datetime(2015, 10, 10, 13) in etp, is_(False))

    def test_timestamp_in_simple_recursive_event(self):
        etp = CalendarTimePeriod(Event.from_ical("""BEGIN:VEVENT
DTSTART:20151010T100000Z
DTEND:20151010T120000Z
CREATED:20151010T100000Z
RRULE:FREQ=DAILY;COUNT=2
UID:123456
END:VEVENT"""))

        assert_that(etp.begin(), is_(datetime(2015, 10, 10, 10, tzinfo=pytz.utc)))
        assert_that(etp.end(), is_(datetime(2015, 10, 10, 12, tzinfo=pytz.utc)))

        assert_that(datetime(2015, 10, 10, 11) in etp, is_(True))
        assert_that(datetime(2015, 10, 10, 9) in etp, is_(False))
        assert_that(datetime(2015, 10, 10, 13) in etp, is_(False))


        assert_that(datetime(2015, 10, 11, 11) in etp, is_(True))
        assert_that(datetime(2015, 10, 11, 9) in etp, is_(False))
        assert_that(datetime(2015, 10, 11, 13) in etp, is_(False))

        assert_that(datetime(2015, 10, 12, 11) in etp, is_(False))

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

        assert_that(etp.begin(), is_(datetime(2015, 10, 10, 10, tzinfo=pytz.utc)))
        assert_that(etp.end(), is_(datetime(2015, 10, 10, 12, tzinfo=pytz.utc)))

        assert_that(datetime(2015, 10, 10, 11) in etp, is_(True))
        assert_that(datetime(2015, 10, 10, 9) in etp, is_(False))
        assert_that(datetime(2015, 10, 10, 13) in etp, is_(False))

        assert_that(datetime(2015, 10, 11, 11) in etp, is_(False))
        assert_that(datetime(2015, 10, 12, 11) in etp, is_(False))
        assert_that(datetime(2015, 10, 13, 11) in etp, is_(False))

        assert_that(datetime(2015, 10, 14, 11) in etp, is_(True))

        assert_that(datetime(2015, 10, 15, 11) in etp, is_(False))

