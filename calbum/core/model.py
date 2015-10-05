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
import filecmp
import locale
import os

from dateutil import tz


class MediaFactory(object):

    def __init__(self, *factories):
        self.factories = factories

    def __call__(self, path):
        return next((
            f(path) for f in self.factories
            if path.lower().endswith(f.file_extensions)), None)


class FileSystemElement(object):

    def __init__(self, path):
        pref_enc = locale.getpreferredencoding()
        if isinstance(path, unicode):
            self._path = path
        else:
            self._path = path.decode(pref_enc)

    def move_to(self, path_prefix):
        """
        Move the file to a new path prefix.  The file extension must not be
        part of path_prefix as it is added by this method using the
        file_extension method.
        :param path_prefix: the destination path without extension
        """
        path = get_destination_path(
            source=self.path(),
            dest=path_prefix,
            extension=self.file_extension())
        if not os.path.exists(path):
            os.renames(self._path, path)
        elif self._path != path:
            os.remove(self._path)
        self._path = path

    def link_to(self, path_prefix):
        """
        Link the file to a new path prefix.  The file extension must not be
        part of path_prefix as it is added by this method using the
        file_extension method.
        :param path_prefix: the destination path without extension
        """
        dest_link_path = get_destination_path(
            source=self.path(),
            dest=path_prefix,
            extension=self.file_extension())
        if not os.path.exists(dest_link_path):
            parent, _ = os.path.split(path_prefix)
            if parent and not os.path.exists(parent):
                os.makedirs(parent)
            try:
                os.link(self._path, dest_link_path)
            except os.error:
                relative_src_path = os.path.join(
                    os.path.relpath(
                        os.path.dirname(self._path),
                        os.path.dirname(dest_link_path)),
                    os.path.basename(self._path))
                os.symlink(relative_src_path, dest_link_path)

    def path(self):
        """
        Return file path (including file extension)
        """
        return self._path

    def file_extension(self):
        """
        Return the actual or required file extension.
        """
        _, file_extension = os.path.splitext(self.path())
        return file_extension


def file_exist_as_symlink(path):
    """Test whether a path exists.  Returns False for broken symbolic links"""
    try:
        os.stat(path)
    except os.error:
        return False
    return True



class Location(object):
    pass


# noinspection PyAbstractClass
class Media(FileSystemElement):
    file_extensions = ()
    time_zone = tz.gettz()

    def location(self):
        """
        :rtype: Location
        """
        raise NotImplemented()

    def timestamp(self):
        """
        Return the creation timestamp of the media.  The name is parsed to be
        used as a date/time.  If it is not a date, the modification time of
        the file on the file system is used.
        :rtype: datetime
        """
        try:
            _, file_name = os.path.split(self.path())
            return string_to_datetime(file_name, self.time_zone)
        except ValueError:
            return datetime.fromtimestamp(
                timestamp=os.path.getmtime(self.path()),
                tz=self.time_zone
            )

    def file_extension(self):
        """
        Return the required file extension
        """
        if len(self.file_extensions):
            return self.file_extensions[0]
        return super(Media, self).file_extension()


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
    """
    A media collection organized by date.
    """
    media_path_format = "%Y/%Y-%m/%Y-%m-%d-%H-%M-%S"

    def link(self, media):
        """
        Link the media file in this TimeLine MediaCollection.
        :param media: the media file
        """
        new_path = os.path.join(
            self.path(),
            media.timestamp().strftime(self.media_path_format))
        media.link_to(new_path)

    def move(self, media):
        """
        Move the media file in this TimeLine MediaCollection.
        :param media: the media file
        """
        new_path = os.path.join(
            self.path(),
            media.timestamp().strftime(self.media_path_format))
        media.move_to(new_path)

    def organize(self):
        """
        Reorganize he files in this TimeLine MediaCollection using the
        configured media path format.
        """
        for media in self:
            self.move(media)


# noinspection PyAbstractClass
class Album(FileSystemElement):
    """
    A file element created by an event that contains a timeline media
    collection.
    """
    timeline_factory = TimeLine

    def title(self):
        """
        Returns the title of the album.
        """
        _, name = os.path.split(self.path())
        return name

    def locations(self):
        """
        :rtype: Location
        """
        raise NotImplementedError()

    def timeline(self):
        """
        Return the media collection organized by date.
        :rtype: TimeLine
        """
        if not hasattr(self, '_timeline'):
            self._timeline = self.timeline_factory(path=self.path())
        return self._timeline

    @classmethod
    def from_event(cls, event, root_path):
        """
        Create the album in the specified root_path using the provided event.
        :rtype: Album
        """
        file_safe_title = ''.join(
            c for c in event.title() if c not in '\/:*?<>|').strip(' .')
        return cls(os.path.join(root_path, file_safe_title))


class TimePeriod(object):
    """
    Represents a block of time with a start date/time and a duration that may
    be recurrent or not.
    """

    def start(self):
        """
        Get the beginning or the first occurrence of this time period.
        :return: start of this time period as a datetime.
        :rtype: datetime.datetime
        """
        raise NotImplementedError()

    def duration(self):
        """
        Get the duration of the first occurrence of this time period.
        :return: duration of the first occurrence of this time period.
        :rtype: datetime.timedelta
        """
        raise NotImplementedError()

    def __contains__(self, timestamp):
        """
        Checks if the time period includes a specific timestamp.
        :param timestamp: a timezone aware datetime
        :return: if the timestamp is included
        """
        raise NotImplementedError()


class Event(object):
    """
    Represents a calendar event with a title and a time period.
    """

    def title(self):
        """
        Returns the title of the event.
        """
        raise NotImplementedError()

    def time_period(self):
        """
        Returns the time period of this event.
        :rtype TimePeriod
        """
        raise NotImplementedError()

    def location(self):
        """
        :rtype Location
        """
        raise NotImplementedError()

    def save_to(self, folder):
        """
        Save this event in the provided folder.
        :param folder: The folder where the event will be saved
        """
        raise NotImplementedError()


def is_same_file(source, dest):
    return os.path.samefile(source, dest) or \
              filecmp.cmp(source, dest, shallow=False)


def get_destination_path(source, dest, extension, suffix=0):
    if suffix:
        computed_dest = u'{}({}){}'.format(dest, suffix, extension)
    else:
        computed_dest = u'{}{}'.format(dest, extension)
    if os.path.exists(computed_dest):
        if is_same_file(source, computed_dest):
            return computed_dest
        return get_destination_path(
            source=source, dest=dest, extension=extension, suffix=suffix+1)
    return computed_dest


def string_to_datetime(string, tzinfo):
    date_string = ''.join(c for c in string if c.isdigit())[0:14]
    if len(date_string) != 14:
        raise ValueError('time data in "{}" must contain 14 digits'.format(string))
    dt = datetime.strptime(date_string, '%Y%m%d%H%M%S')
    return dt.replace(tzinfo=tzinfo)
