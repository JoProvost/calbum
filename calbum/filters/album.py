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

    def __init__(self, albums_path, events):
        self.events = events
        self.albums_path = albums_path
 
    def best_album_for(self, picture):
        for event in self.events:
            if picture.timestamp() in event.time_period():
                album = self.album_factory.from_event(event, self.albums_path)
                return album

    def move_picture(self, picture):
        album = self.best_album_for(picture)
        if album:
            album.timeline().move_picture(picture)

    def link_picture(self, picture):
        album = self.best_album_for(picture)
        if album:
            album.timeline().move_picture(picture)


def link_in_albums(inbox_path, albums_path, calendar_url):
    pictures = image.get_pictures_from_path(inbox_path)
    filter = CalendarAlbumFilter(albums_path, calendar_url)

    for picture in pictures:
        filter.link_picture(picture)
