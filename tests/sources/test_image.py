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
import unittest

from dateutil import tz
from hamcrest import assert_that, is_
from calbum.core.model import TimeLine

from calbum.sources.image import JpegPicture
from tests import resources


class TestExifPicture(unittest.TestCase):
    def test_exif(self):
        assert_that(
            JpegPicture(resources.file_path('image-01.jpeg')).timestamp(),
            is_(datetime(2012, 5, 1, 1, 0, 0, tzinfo=tz.gettz())))


class TestExifTimeLine(unittest.TestCase):
    def test_timeline_organize_pictures(self):
        _, inbox_path = resources.copytree()
        timeline = TimeLine(inbox_path)

        timeline.organize()

        for name, file_details in resources.files.iteritems():
            file_path = os.path.join(inbox_path, file_details['expected_path'])
            assert_that(
                os.path.exists(file_path),
                is_(True),
                'File is missing: {} -> {}'.format(name, file_path))
            assert_that(
                resources.md5sum(file_path),
                is_(file_details['md5sum']),
                'wrong md5sum for {} at {}'.format(name, file_path)
            )

