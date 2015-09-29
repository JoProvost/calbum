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

import argparse
import sys
from dateutil.tz import gettz

from progress.bar import ChargingBar

from calbum.core import model
from calbum.filters import timeline, album
from calbum.sources import image, calendar, exiftool

model.MediaCollection.media_factory = model.MediaFactory(
    image.JpegPicture,
    image.TiffPicture,
    exiftool.VideoMP4Media,
    exiftool.Video3GPMedia,
)

def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        prog='calbum',
        add_help=True,
        description='calbum is an unattended calendar-based photo organiser. '
                    'It is meant to allow easy management of pictures based '
                    'on their location, date and calendar events without '
                    'the need of a database or a special browser to retrieve '
                    'them.')

    parser.add_argument('--inbox',
                        help='The path of the inbox directory. '
                             '(default: ./inbox)',
                        metavar='path',
                        default='./inbox')

    parser.add_argument('--timeline',
                        help='The path of the timeline directory. '
                             '(default: ./timeline)',
                        metavar='path',
                        default='./timeline')

    parser.add_argument('--album',
                        help='The path of the album directory. '
                             '(default: ./album)',
                        metavar='path',
                        default='./album')

    parser.add_argument('--calendar',
                        help='The url of the album calendar. (ical)',
                        metavar='url')

    parser.add_argument('--date-format',
                        help='The format to use for timestamps.',
                        metavar='format',
                        default=model.TimeLine.media_path_format)

    parser.add_argument('--save-events',
                        help='Keep the calendar event in the album.',
                        action='store_true')

    parser.add_argument('--time-zone',
                        metavar='tz',
                        help='Pictures timezone (default to local time).')

    settings = vars(parser.parse_args(args))

    model.TimeLine.media_path_format = settings['date_format']
    model.Media.time_zone = gettz(settings['time_zone'])

    filters = [timeline.TimelineFilter(settings['timeline']).move]
    if settings['calendar']:
        events = calendar.CalendarEvent.load_from_url(url=settings['calendar'])
        filters.append(album.CalendarAlbumFilter(
            albums_path=settings['album'],
            events=events,
            save_events=settings['save_events']
        ).link)

    suffix = '%(index)d/%(max)d [eta: %(eta)ds]'
    bar = ChargingBar('Processing inbox:', suffix=suffix)
    for picture in bar.iter(list(model.MediaCollection(settings['inbox']))):
        for action in filters:
            action(picture)
