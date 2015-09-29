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

import subprocess

from calbum.core.model import Media, string_to_datetime


class ExifToolMedia(Media):
    file_extensions = ()

    exiftool_path = 'exiftool'
    timestamp_tags = (
        'Creation Date',
        'Date/Time Original'
        'Track Create Date',
        'Media Create Date',
        'Create Date',
    )

    def exif(self):
        if not hasattr(self, '_exif'):
            self._exif = {}
            try:
                for line in subprocess.check_output(
                        ["exiftool", self.path()]).splitlines():
                    key, value = line.split(':', 1)
                    self._exif[key.strip()] = value.strip()
            except subprocess.CalledProcessError:
                pass
        return self._exif

    def timestamp(self):
        """
        Return the creation timestamp of the media as defined in the EXIF
        metadata ('Creation Date', 'Date/Time Original', 'Track Create Date',
        'Media Create Date', 'Create Date')
        :rtype: datetime
        """
        try:
            exif = self.exif()
            d = next((
                string_to_datetime(str(exif[tag]), self.time_zone)
                for tag in self.timestamp_tags if tag in exif), None)
            if d and (d.tzinfo is None or d.tzinfo.utcoffset(d) is None):
                d = d.replace(tzinfo=self.time_zone)
            if d:
                return d
        except ValueError:
            pass

        return super(ExifToolMedia, self).timestamp()

    def location(self):
        raise NotImplemented()


class JpegPicture(ExifToolMedia):
    file_extensions = ('.jpeg', '.jpg')


class TiffPicture(ExifToolMedia):
    file_extensions = ('.tiff', '.tif')


class VideoMP4Media(ExifToolMedia):
    file_extensions = ('.mp4',)


class Video3GPMedia(ExifToolMedia):
    file_extensions = ('.3gp', '.3g2')
