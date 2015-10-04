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

import unittest
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
        get_destination_path.return_value = 'dest/path.jpg'
        exists.return_value = False
        link.side_effect = IOError()

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
        symlink.assert_called_with('origin/path.jpg', 'dest/path.jpg')
        assert_that(remove.called, is_(False))

    def test_file_extension_based_on_path(self):
        fse = model.FileSystemElement('some/file/path.pdf')
        assert_that(fse.file_extension(), is_('.pdf'))


class TestMedia(unittest.TestCase):

    def test_file_extension_based_on_path(self):
        fse = model.Media('some/file/path.pdf')
        assert_that(fse.file_extension(), is_('.pdf'))

    def test_file_extension_based_on_class(self):
        class FakeGifMedia(model.Media):
            file_extensions = ('.gif', '.gifa')
        fse = FakeGifMedia('some/file/path.pdf')
        assert_that(fse.file_extension(), is_('.gif'))
