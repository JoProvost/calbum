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

    def __init__(self, event):
        """
        :type event: icalendar.Event
        """
        self.event = event
        self.rule = None

    def begin(self):
        return self.event['dtstart'].dt

    def end(self):
        return self.event.get('dtend', self.event['dtstart']).dt

    def recurrent(self):
        if self.rule is None:
            if 'rrule' in self.event:
                self.rule = dateutil.rrule.rruleset()
                self.rule.rrule(dateutil.rrule.rrulestr(
                    self.event['rrule'].to_ical(), dtstart=self.begin()))
                for dt in get_datetime_list(self.event.get('exdate', [])):
                    self.rule.exdate(dt)
        return self.rule

    def __contains__(self, timestamp):
        start = self.begin()
        end = self.end()
        rule = self.recurrent()

        if not hasattr(start, 'tzinfo'):
            timestamp = timestamp.replace(tzinfo=None)

        if rule is not None:
            delta = end - start
            start = rule.before(timestamp, True) or start
            end = start + delta

        if not hasattr(start, 'tzinfo'):
            timestamp = datetime.date(timestamp.year, timestamp.month, timestamp.day)

        return start <= timestamp < end


class CalendarEvent(Event):
    def __init__(self, event):
        """
        :type event: icalendar.Event
        """
        self._event = event
        self._time_period = CalendarTimePeriod(self._event)

    def title(self):
        return self._event['summary']

    def time_period(self):
        return self._time_period

    def location(self):
        raise NotImplementedError()

    def save_to(self, path):
        event_path = os.path.join(path, 'event.ics')
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
        events=[]
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
