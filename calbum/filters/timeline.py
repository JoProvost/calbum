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

from calbum.filters import PictureFilter
from calbum.sources import image


class TimelineFilter(PictureFilter):
    timeline_factory = image.ExifTimeLine

    def __init__(self, timeline_path):
        self.timeline = self.timeline_factory(timeline_path)

    def move_picture(self, picture):
        self.timeline.move_picture(picture)

    def link_picture(self, picture):
        self.timeline.link_picture(picture)


def move_in_timeline(inbox_path, timeline_path):
    pictures = image.get_pictures_from_path(inbox_path)
    filter = TimelineFilter(timeline_path)

    for picture in pictures:
        filter.move_picture(picture)
