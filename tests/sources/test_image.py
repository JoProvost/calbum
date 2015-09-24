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
from hamcrest import assert_that, is_
import re

from calbum.sources.image import ExifTimeLine, ExifPicture, get_pictures_from_path

from tests import resources


class TestExifPicture(unittest.TestCase):
    def test_exif(self):
        assert_that(
            ExifPicture(resources.file_path('image-01.jpeg')).timestamp(),
            is_(datetime(2012, 05, 01, 01, 0, 0)))


class TestExifTimeLine(unittest.TestCase):
    def test_timeline_organize_pictures(self):
        timeline_path = resources.copytree()
        timeline = ExifTimeLine(timeline_path)

        timeline.organize()

        for name, file_details in resources.files.iteritems():
            file_path = os.path.join(timeline_path, file_details['expected_path'])
            assert_that(
                resources.md5sum(file_path),
                is_(file_details['md5sum']),
                'wrong md5sum for {} at {}'.format(name, file_path)
            )


class TestModule(unittest.TestCase):
    def test_get_pictures_from_path(self):
        collection_path = resources.copytree()
        pictures = list(get_pictures_from_path(collection_path))

        assert_that(len(pictures), is_(len(resources.files)))

        for picture in pictures:
            folder, name = os.path.split(picture.path())
            date_string = resources.files[name]['date_time']
            expected_date = datetime(
                *[int(p) for p in re.split('[ :]', date_string)])

            assert_that(
                folder,
                is_(collection_path),
                'wrong path for {}'.format(name))
            assert_that(
                picture.timestamp(),
                is_(expected_date),
                'wrong timestamp for {}'.format(name))