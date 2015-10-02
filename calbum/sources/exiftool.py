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
import logging

import subprocess

from calbum.core.model import Media, string_to_datetime

exiftool_path = 'exiftool'


class ExifToolMedia(Media):
    file_extensions = ()

    timestamp_tags = (
        'Creation Date',
        'Date/Time Original',
        'Track Create Date',
        'Media Create Date',
        'Create Date',
    )

    def exif(self):
        if not hasattr(self, '_exif'):
            self._exif = {}
            try:
                for line in subprocess.check_output(
                        [exiftool_path, self.path()]).splitlines():
                    key, value = line.split(':', 1)
                    self._exif[key.strip()] = value.strip()
            except OSError as e:
                logging.warning('Metadata processing with "{}" '
                                'failed for "{}": {}'.format(
                    exiftool_path, self.path(), repr(e)))
            except subprocess.CalledProcessError as e:
                logging.warning('Metadata processing with "{}" '
                                'failed for "{}": {}'.format(
                    exiftool_path, self.path(), repr(e)))
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
            if d:
                if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
                    d = d.replace(tzinfo=self.time_zone)
                if d.year < 1970:
                    logging.info('Patched incorrect time offset, for {} '
                                 'see https://trac.ffmpeg.org/ticket/1471'
                                 .format(self.path()))
                    # See https://trac.ffmpeg.org/ticket/1471
                    d = d.replace(year=d.year+66)
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
