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
from hamcrest import assert_that, is_
import mock

from calbum.core import model


class TestFileSystemElement(unittest.TestCase):

    @mock.patch('os.renames')
    @mock.patch('os.remove')
    @mock.patch('os.path.exists')
    @mock.patch('calbum.core.model.get_destination_path')
    def test_move_to(self, get_destination_path, exists, remove, renames):
        get_destination_path.return_value = 'dest/path.jpg'
        exists.return_value = False

        fse = model.FileSystemElement('origin/path.jpg')
        fse.move_to('dest/path')
        assert_that(fse.path(), is_('dest/path.jpg'))

        get_destination_path.assert_called_with(
            source='origin/path.jpg', dest='dest/path', extension='.jpg')
        exists.assert_called_with('dest/path.jpg')
        renames.assert_called_with('origin/path.jpg', 'dest/path.jpg')
        assert_that(remove.called, is_(False))

    @mock.patch('os.renames')
    @mock.patch('os.remove')
    @mock.patch('os.path.exists')
    @mock.patch('calbum.core.model.get_destination_path')
    def test_move_to_same_file(self, get_destination_path, exists, remove, renames):
        get_destination_path.return_value = 'dest/path.jpg'
        exists.return_value = True

        fse = model.FileSystemElement('origin/path.jpg')
        fse.move_to('dest/path')
        assert_that(fse.path(), is_('dest/path.jpg'))

        get_destination_path.assert_called_with(
            source='origin/path.jpg', dest='dest/path', extension='.jpg')
        exists.assert_called_with('dest/path.jpg')
        remove.assert_called_with('origin/path.jpg')
        assert_that(renames.called, is_(False))

    @mock.patch('os.link')
    @mock.patch('os.makedirs')
    @mock.patch('os.remove')
    @mock.patch('os.path.exists')
    @mock.patch('calbum.core.model.get_destination_path')
    def test_link_to(self, get_destination_path, exists, remove, makedirs, link):
        get_destination_path.return_value = 'dest/path.jpg'
        exists.return_value = False

        fse = model.FileSystemElement('origin/path.jpg')
        fse.link_to('dest/path')
        assert_that(fse.path(), is_('origin/path.jpg'))

        get_destination_path.assert_called_with(
            source='origin/path.jpg', dest='dest/path', extension='.jpg')
        exists.assert_has_calls([
           mock.call('dest/path.jpg'),
           mock.call('dest'),
        ])
        makedirs.assert_called_with('dest')
        link.assert_called_with('origin/path.jpg', 'dest/path.jpg')
        assert_that(remove.called, is_(False))

    @mock.patch('os.link')
    @mock.patch('os.remove')
    @mock.patch('os.path.exists')
    @mock.patch('calbum.core.model.get_destination_path')
    def test_link_to_same_file(self, get_destination_path, exists, remove, link):
        get_destination_path.return_value = 'dest/path.jpg'
        exists.return_value = True

        fse = model.FileSystemElement('origin/path.jpg')
        fse.link_to('dest/path')
        assert_that(fse.path(), is_('origin/path.jpg'))

        get_destination_path.assert_called_with(
            source='origin/path.jpg', dest='dest/path', extension='.jpg')
        exists.assert_called_with('dest/path.jpg')
        assert_that(link.called, is_(False))
        assert_that(remove.called, is_(False))

    @mock.patch('os.symlink')
    @mock.patch('os.link')
    @mock.patch('os.makedirs')
    @mock.patch('os.remove')
    @mock.patch('os.path.exists')
    @mock.patch('calbum.core.model.get_destination_path')
    def test_link_to_make_symlink_on_error(self, get_destination_path, exists, remove, makedirs, link, symlink):
        get_destination_path.return_value = 'dest/new_name.jpg'
        exists.return_value = False
        link.side_effect = OSError()

        fse = model.FileSystemElement('\xc3\x80 trier/origin/path.jpg')
        fse.link_to('dest/new_name')
        assert_that(fse.path(), is_(u'\xc0 trier/origin/path.jpg'))

        get_destination_path.assert_called_with(
            source=u'\xc0 trier/origin/path.jpg', dest='dest/new_name', extension='.jpg')
        exists.assert_has_calls([
            mock.call('dest/new_name.jpg'),
            mock.call('dest'),
            ])
        makedirs.assert_called_with('dest')
        link.assert_called_with(u'\xc0 trier/origin/path.jpg', 'dest/new_name.jpg')
        symlink.assert_called_with(u'../\xc0 trier/origin/path.jpg', 'dest/new_name.jpg')
        assert_that(remove.called, is_(False))

    def test_file_extension_based_on_path(self):
        fse = model.FileSystemElement('some/file/path.pdf')
        assert_that(fse.file_extension(), is_('.pdf'))


class TestGetDestinationPath(unittest.TestCase):

    @mock.patch('os.path.exists')
    def test_get_destination_path_file_doesnt_exist(self, exists):
        exists.return_value = False
        assert_that(
            model.get_destination_path(
                source='origin/path.jpg', dest='dest/path', extension='.jpg'),
            is_('dest/path.jpg'))
        exists.assert_called_with('dest/path.jpg')

    @mock.patch('filecmp.cmp')
    @mock.patch('os.path.samefile')
    @mock.patch('os.path.exists')
    def test_get_destination_path_file_exist_with_different_file(self, exists, samefile, filecmp):
        samefile.return_value = False
        filecmp.return_value = False
        exists.side_effect = [
            True,
            False
        ]
        assert_that(
            model.get_destination_path(
                source='origin/path.jpg', dest='dest/path', extension='.jpg'),
            is_('dest/path(1).jpg'))
        exists.has_calls([
            mock.call('dest/path.jpg'),
            mock.call('dest/path(1).jpg'),
        ])

    @mock.patch('filecmp.cmp')
    @mock.patch('os.path.samefile')
    @mock.patch('os.path.exists')
    def test_get_destination_path_file_exist_with_different_file_twice(self, exists, samefile, filecmp):
        samefile.return_value = False
        filecmp.return_value = False
        exists.side_effect = [
            True,
            True,
            False
        ]
        assert_that(
            model.get_destination_path(
                source='origin/path.jpg', dest='dest/path', extension='.jpg'),
            is_('dest/path(2).jpg'))
        exists.has_calls([
            mock.call('dest/path.jpg'),
            mock.call('dest/path(1).jpg'),
            mock.call('dest/path(2).jpg'),
        ])

    @mock.patch('filecmp.cmp')
    @mock.patch('os.path.samefile')
    @mock.patch('os.path.exists')
    def test_get_destination_path_file_exist_with_same_file_inode(self, exists, samefile, filecmp):
        samefile.return_value = True
        filecmp.return_value = False
        exists.side_effect = [
            True
        ]
        assert_that(
            model.get_destination_path(
                source='origin/path.jpg', dest='dest/path', extension='.jpg'),
            is_('dest/path.jpg'))
        exists.has_calls([
            mock.call('dest/path.jpg'),
        ])

    @mock.patch('filecmp.cmp')
    @mock.patch('os.path.samefile')
    @mock.patch('os.path.exists')
    def test_get_destination_path_file_exist_with_same_file_content(self, exists, samefile, filecmp):
        samefile.return_value = False
        filecmp.return_value = True
        exists.side_effect = [
            True
        ]
        assert_that(
            model.get_destination_path(
                source='origin/path.jpg', dest='dest/path', extension='.jpg'),
            is_('dest/path.jpg'))
        exists.has_calls([
            mock.call('dest/path.jpg'),
        ])


class TestMedia(unittest.TestCase):

    def test_file_extension_based_on_path(self):
        fse = model.Media('some/file/path.pdf')
        assert_that(fse.file_extension(), is_('.pdf'))

    def test_file_extension_based_on_class(self):
        class FakeGifMedia(model.Media):
            file_extensions = ('.gif', '.gifa')
        fse = FakeGifMedia('some/file/path.pdf')
        assert_that(fse.file_extension(), is_('.gif'))

    def test_timestamp_based_on_filename(self):
        media = model.Media('some/file/VID_20120501_224323.avi')
        assert_that(
            media.timestamp(),
            is_(datetime(2012, 5, 1, 22, 43, 23, tzinfo=tz.gettz())))
