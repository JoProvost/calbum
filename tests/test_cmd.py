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

import os
import unittest

from hamcrest import assert_that, is_

from calbum import cmd
from calbum.sources.image import ExifPicturesCollection
from tests import resources


class TestMain(unittest.TestCase):
    def test_main(self):
        repo_path, inbox_path = resources.copytree()
        timeline_path = os.path.join(repo_path, 'timeline')
        album_path = os.path.join(repo_path, 'album')

        os.chdir(repo_path)
        cmd.main([
            '--inbox', inbox_path,
            '--calendar', 'https://raw.githubusercontent.com/JoProvost/calbum/master/tests/resources/calendar.ics',
            '--save-events'
        ])

        timeline = ExifPicturesCollection(timeline_path)
        pictures = list(timeline)

        assert_that(len(pictures), is_(len(resources.files)))

        for name, file_details in resources.files.iteritems():
            file_path = os.path.join(
                timeline_path, file_details['expected_path'])
            assert_that(
                resources.md5sum(file_path),
                is_(file_details['md5sum']),
                'wrong md5sum for {} at {}'.format(name, file_path)
            )

            if file_details['event_name']:
                file_path = os.path.join(
                    album_path, file_details['event_name'],
                    file_details['expected_path'])
                assert_that(
                    resources.md5sum(file_path),
                    is_(file_details['md5sum']),
                    'wrong md5sum for {} at {}'.format(name, file_path)
                )
