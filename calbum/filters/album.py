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

from calbum.core import model
from calbum.filters import MediaFilter


class CalendarAlbumFilter(MediaFilter):

    def __init__(self, albums_path, events, save_events):
        self.events = list(events)
        self.albums_path = albums_path
        self.save_events = save_events
 
    def albums_for(self, media):
        for event in self.events:
            if media.timestamp() in event.time_period():
                yield (model.Album.from_event(event, self.albums_path),
                       event)

    def move(self, media):
        album, event = next(self.albums_for(media), (None, None))
        if album:
            album.timeline().move(media)
            if self.save_events:
                event.save_to(album.path())

    def link(self, media):
        for album, event in self.albums_for(media):
            album.timeline().link(media)
            if self.save_events:
                event.save_to(album.path())

