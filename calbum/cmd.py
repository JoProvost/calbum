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

from calbum.core.model import TimeLine
from calbum.filters import timeline_filter


def main():
    parser = argparse.ArgumentParser(
        prog='calbum',
        add_help=True,
        description='Calendar-based photo organiser (only timeline for now).')

    parser.add_argument('--inbox',
                        help='The path of the inbox directory.',
                        metavar='path',
                        required=True)

    parser.add_argument('--timeline',
                        help='The path of the timeline directory.',
                        metavar='path',
                        required=True)

    parser.add_argument('--date-format',
                        help='The format to use for timestamps.',
                        default=TimeLine.pictures_path_format)

    args = vars(parser.parse_args())

    if 'date_format' in args:
        TimeLine.pictures_path_format = args['date_format']

    timeline_filter.move_in_timeline(
        inbox_path=args['inbox'],
        timeline_path=args['timeline']
    )
