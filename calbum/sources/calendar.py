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

import urllib2
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
        return self.event['dtend'].dt

    def recurrent(self):
        if self.rule is None:
            if 'rrule' in self.event:
                rrulestr = '\n'.join(
                    ['RRULE:' + self.event['rrule'].to_ical()] +
                    ['EXDATE:'+s.to_ical() for s in self.event.get('exdate', [])])
                self.rule = dateutil.rrule.rrulestr(rrulestr, dtstart=self.begin())
        return self.rule

    def __contains__(self, timestamp):
        start = self.begin()
        end = self.end()
        if timestamp.tzinfo and start.tzinfo:
            localized_timestamp = start.tzinfo.localize(timestamp)
        else:
            localized_timestamp = timestamp.replace(tzinfo=start.tzinfo)
        rule = self.recurrent()
        if rule is not None:
            delta = end - start
            start = rule.before(localized_timestamp, True) or start
            end = start + delta
        return start <= localized_timestamp <= end


class CalendarEvent(Event):
    def __init__(self, event):
        """
        :type event: icalendar.Event
        """
        self.event = event

    def title(self):
        return self.event['summary']

    def time_period(self):
        if not hasattr(self, '_time_period'):
            self._time_period = self._time_period or CalendarTimePeriod(self.event)
        return self._time_period

    def location(self):
        raise NotImplementedError()


def get_events_from_url(url):
    response = urllib2.urlopen(url)
    if response.code != 200:
        raise Exception("Something went wrong. HTTP response code: %s" % response.code)
    ical_data = response.read().decode('UTF-8')
    return get_events_from_ical(ical_data)


def get_events_from_ical(ical_data):
    events_tp = []
    cal = icalendar.Calendar.from_ical(ical_data)
    for component in cal.walk():
        if component.name == "VEVENT":
            events_tp.append(CalendarEvent(component))
    return events_tp