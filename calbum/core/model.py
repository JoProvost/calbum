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
import os
from dateutil import tz


class MediaFactory(object):

    def __init__(self, *factories):
        self.factories = factories

    def __call__(self, path):
        return next((
            f(path) for f in self.factories
            if path.lower().endswith(f.file_types)), None)


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
class Media(FileSystemElement):
    file_types = ()
    time_zone = tz.gettz()

    def location(self):
        raise NotImplemented()

    def timestamp(self):
        return datetime.fromtimestamp(
            timestamp=os.path.getctime(self.path()),
            tz=self.time_zone
        )

    def move_to(self, path):
        if not path.lower().endswith(self.file_types) and self.file_types:
            path = path + self.file_types[0]
        super(Media, self).move_to(path=path)

    def link_to(self, path):
        if not path.lower().endswith(self.file_types) and self.file_types:
            path = path + self.file_types[0]
        super(Media, self).link_to(path=path)



# noinspection PyAbstractClass
class MediaCollection(FileSystemElement):
    media_factory = Media

    def __iter__(self):
        for sub_path, subdirs, files in os.walk(self.path()):
            for name in files:
                media = self.media_factory(os.path.join(sub_path, name))
                if media is not None:
                    yield media


# noinspection PyAbstractClass
class TimeLine(MediaCollection):
    media_path_format = "%Y/%Y-%m/%Y-%m-%d-%H-%M-%S"

    def link(self, media):
        new_path = os.path.join(
            self.path(),
            media.timestamp().strftime(self.media_path_format))
        media.link_to(new_path)

    def move(self, media):
        new_path = os.path.join(
            self.path(),
            media.timestamp().strftime(self.media_path_format))
        media.move_to(new_path)

    def organize(self):
        for picture in self:
            self.move(picture)


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