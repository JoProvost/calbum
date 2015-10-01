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
import unittest

from dateutil import tz
from hamcrest import assert_that, is_, instance_of
from calbum.sources import exiftool

from tests import resources


class TestExifToolMedia(unittest.TestCase):
    def setUp(self):
        self.exiftool_path = exiftool.exiftool_path

    def tearDown(self):
        exiftool.exiftool_path = self.exiftool_path

    def test_jpeg_timestamp(self):
        assert_that(
            exiftool.JpegPicture(resources.file_path('image-01.jpeg')).timestamp(),
            is_(datetime(2012, 5, 1, 1, 0, 0, tzinfo=tz.gettz())))

    def test_tiff_timestamp(self):
        assert_that(
            exiftool.TiffPicture(resources.file_path('image-03.tif')).timestamp(),
            is_(datetime(2013, 2, 1, 3, 0, 0, tzinfo=tz.gettz())))

    def test_mp4_timestamp(self):
        assert_that(
            exiftool.VideoMP4Media(resources.file_path('video-01.mp4')).timestamp(),
            is_(datetime(2014, 1, 1, 19, 30, 0, tzinfo=tz.gettz())))

    def test_3gp_timestamp(self):
        assert_that(
            exiftool.Video3GPMedia(resources.file_path('video-02.3gp')).timestamp(),
            is_(datetime(2014, 2, 2, 19, 30, 0, tzinfo=tz.gettz())))

    def test_mp4_timestamp_without_exiftool(self):
        try:
            exiftool.ExifToolMedia.exiftool_path = '__invalid_command__'
            assert_that(
                exiftool.VideoMP4Media(resources.file_path('video-01.mp4')).timestamp(),
                instance_of(datetime))
        except Exception as e:
            raise AssertionError('Expected no exception but raised {}'.format(e))
