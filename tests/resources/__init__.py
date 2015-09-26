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
import hashlib
import shutil
import tempfile

import yaml


def file_path(file_name):
    return os.path.join(os.path.dirname(__file__), file_name)


def copytree():
    tmp_folder = tempfile.mkdtemp()
    inbox_path = os.path.join(tmp_folder, 'inbox')
    shutil.copytree(os.path.dirname(__file__), inbox_path)
    return tmp_folder, inbox_path


def md5sum(filename):
    with open(filename,"rb") as fd:
        return hashlib.md5(fd.read()).hexdigest()


files = yaml.safe_load(open(file_path('images.yaml')))
