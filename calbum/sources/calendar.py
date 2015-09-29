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

import os

import urllib2
import datetime

import dateutil
import dateutil.rrule
import icalendar

from calbum.core.model import TimePeriod, Event


class CalendarTimePeriod(TimePeriod):
    """
    Represents an icalendar vevent block of time with a start date/time and a
    duration that may be recurrent or not.
    """

    default_duration = datetime.timedelta()

    def __init__(self, event):
        """
        :type event: icalendar.Event
        """
        self._event = event
        self._recurrence = None

    def start(self):
        """
        Get the beginning or the first occurrence of this time period.
        :return: start of this time period as a datetime.
        :rtype: datetime.datetime
        """
        return self._event['dtstart'].dt

    def duration(self):
        """
        Get the duration of the first occurrence of this time period.
        :return: duration of the first occurrence of this time period.
        :rtype: datetime.timedelta
        """
        duration = self._event.get('duration')
        end = self._event.get('dtend')
        if duration:
            return duration.dt
        if end:
            return end.dt - self.start()
        return self.default_duration

    def recurrence(self):
        """
        Get the recurrence rules (with the exceptions).
        :return: the recurrence rules
        :rtype: dateutil.rrule.rruleset
        """
        if self._recurrence is None:
            if 'rrule' in self._event:
                self._recurrence = dateutil.rrule.rruleset()
                self._recurrence.rrule(dateutil.rrule.rrulestr(
                    self._event['rrule'].to_ical(), dtstart=self.start()))
                for dt in get_datetime_list(self._event.get('exdate', [])):
                    self._recurrence.exdate(dt)
        return self._recurrence

    def __contains__(self, timestamp):
        """
        Checks if the time period includes a specific timestamp.
        :param timestamp: a timezone aware datetime
        :return: if the timestamp is included
        """
        start = self.start()
        duration = self.duration()
        rule = self.recurrence()

        if not hasattr(start, 'tzinfo'):
            timestamp = timestamp.replace(tzinfo=None)

        if rule is not None:
            start = rule.before(timestamp, True) or start

        if not hasattr(start, 'tzinfo'):
            timestamp = datetime.date(timestamp.year, timestamp.month, timestamp.day)

        return start <= timestamp < (start+duration)


class CalendarEvent(Event):
    """
    Represents an ical calendar event with a title and a time period.
    """

    def __init__(self, event):
        """
        :type event: icalendar.Event
        """
        self._event = event
        self._time_period = CalendarTimePeriod(self._event)

    def title(self):
        """
        Returns the title of the event (uses the summary field).
        """
        return self._event['summary']

    def time_period(self):
        """
        Returns the time period of this event.
        :rtype TimePeriod
        """
        return self._time_period

    def location(self):
        raise NotImplementedError()

    def save_to(self, folder):
        """
        Save this event in the provided folder (event.ics).
        :param folder: The folder where the event will be saved
        """
        event_path = os.path.join(folder, 'event.ics')
        with open(event_path, 'w') as f:
            cal = icalendar.Calendar()
            cal.add_component(self._event)
            f.write(cal.to_ical())

    @classmethod
    def load_from_file(cls, path):
        with open(path, 'r') as f:
            return cls.load_from_stream(f)

    @classmethod
    def load_from_url(cls, url):
        response = urllib2.urlopen(url)
        if response.code != 200:
            raise Exception("Something went wrong. HTTP response code: %s" % response.code)
        return cls.load_from_stream(response)

    @classmethod
    def load_from_stream(cls, stream):
        events = []
        cal = icalendar.Calendar.from_ical(stream.read().decode('UTF-8'))
        for component in cal.walk():
            if component.name == "VEVENT":
                events.append(cls(event=component))
        return events


def get_datetime_list(obj):
    if not isinstance(obj, list):
        obj = [obj]
    for item in obj:
        if hasattr(item, 'dts'):
            for dt in item.dts:
                yield dt.dt
        else:
            yield item.dt
