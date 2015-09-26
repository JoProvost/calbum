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


from datetime import datetime
from fnmatch import fnmatch
import os
from dateutil import tz

file_types = (
    '.jpg',
    '.jpeg'
)


class FileSystemElement(object):

    def __init__(self, path):
        self._path = path

    def move_to(self, path):
        if path != self.path():
            os.renames(self._path, path)
            self._path = path

    def link_to(self, path):
        if path != self.path():
            parent, name = os.path.split(path)
            if parent and name and not os.path.exists(parent):
                os.makedirs(parent)
            os.link(self._path, path)

    def path(self):
        return self._path


# noinspection PyAbstractClass
class Picture(FileSystemElement):
    time_zone = tz.gettz()

    def location(self):
        raise NotImplemented()

    def timestamp(self):
        return datetime.fromtimestamp(
            timestamp=os.path.getctime(self.path()),
            tz=self.time_zone
        )


# noinspection PyAbstractClass
class PicturesCollection(FileSystemElement):
    pictures_factory = Picture

    def __iter__(self):
        for sub_path, subdirs, files in os.walk(self.path()):
            for name in files:
                if name.lower().endswith(file_types):
                    yield self.pictures_factory(os.path.join(sub_path, name))


# noinspection PyAbstractClass
class TimeLine(PicturesCollection):
    pictures_path_format = "%Y/%Y-%m/%Y-%m-%d-%H-%M-%S.jpeg"

    def link_picture(self, picture):
        new_path = os.path.join(
            self.path(),
            picture.timestamp().strftime(self.pictures_path_format))
        picture.link_to(new_path)

    def move_picture(self, picture):
        new_path = os.path.join(
            self.path(),
            picture.timestamp().strftime(self.pictures_path_format))
        picture.move_to(new_path)

    def organize(self):
        for picture in self:
            self.move_picture(picture)


# noinspection PyAbstractClass
class Album(FileSystemElement):
    timeline_factory = TimeLine

    def title(self):
        _, name = os.path.split(self.path())
        return name

    def locations(self):
        raise NotImplementedError()

    def timeline(self):
        if not hasattr(self, '_timeline'):
            self._timeline = self.timeline_factory(path=self.path())
        return self._timeline

    @classmethod
    def from_event(cls, event, root_path):
        file_safe_title = ''.join(
            c for c in event.title() if c not in '\/:*?<>|').strip(' .')
        return cls(os.path.join(root_path, file_safe_title))


class Event(object):

    def title(self):
        raise NotImplementedError()

    def time_period(self):
        raise NotImplementedError()

    def location(self):
        raise NotImplementedError()

    def save_to(self, path):
        raise NotImplementedError()


class TimePeriod(object):
    def begin(self):
        raise NotImplementedError()

    def end(self):
        raise NotImplementedError()

    def __contains__(self, item):
        raise NotImplementedError()


class Location(object):
    pass