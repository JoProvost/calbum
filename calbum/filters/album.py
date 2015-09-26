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


class CalendarAlbumFilter(PictureFilter):
    album_factory = image.ExifAlbum

    def __init__(self, albums_path, events, save_events):
        self.events = list(events)
        self.albums_path = albums_path
        self.save_events = save_events
 
    def albums_for(self, picture):
        for event in self.events:
            if picture.timestamp() in event.time_period():
                yield (self.album_factory.from_event(event, self.albums_path),
                       event)

    def move_picture(self, picture):
        album, event = next(self.albums_for(picture), (None, None))
        if album:
            album.timeline().move_picture(picture)
            if self.save_events:
                event.save_to(album.path())

    def link_picture(self, picture):
        for album, event in self.albums_for(picture):
            album.timeline().link_picture(picture)
            if self.save_events:
                event.save_to(album.path())

