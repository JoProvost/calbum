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

import exifread

from calbum.core.model import Picture, TimeLine, PicturesCollection, Album


class ExifPicture(Picture):

    exif_datetime_format = '%Y:%m:%d %H:%M:%S'
    timestamp_tags = (
        'Image DateTime',
        'EXIF DateTimeOriginal',
        'EXIF DateTimeDigitized',
        'DateTime'
    )

    def exif(self):
        if not hasattr(self, '_exif'):
            with open(self.path()) as f:
                self._exif = exifread.process_file(f)
        return self._exif

    def timestamp(self):
        exif = self.exif()

        d = next((
            datetime.strptime(str(exif[tag]), self.exif_datetime_format)
            for tag in self.timestamp_tags if tag in exif), None)
        if d and (d.tzinfo is None or d.tzinfo.utcoffset(d) is None):
            d = d.replace(tzinfo=self.time_zone)

        return d or super(ExifPicture, self).timestamp()

    def location(self):
        raise NotImplemented()


class ExifPicturesCollection(PicturesCollection):
    pictures_factory = ExifPicture


class ExifTimeLine(TimeLine, ExifPicturesCollection):
    pass


class ExifAlbum(Album):
    timeline_factory = ExifTimeLine


def get_pictures_from_path(path):
    return iter(ExifPicturesCollection(path))


def get_albums_from_path(path):
    raise NotImplementedError()


def get_time_lines_from_path(path):
    raise NotImplementedError()