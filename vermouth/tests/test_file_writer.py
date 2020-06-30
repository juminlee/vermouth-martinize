# Copyright 2020 University of Groningen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path
import os
import pytest
from vermouth.file_writer import DeferredFileWriter


def test_is_singleton():
    writer1 = DeferredFileWriter()
    writer2 = DeferredFileWriter()

    assert writer1 is writer2


@pytest.mark.parametrize('name, existing_files, expected', [
    ('a', [], []),
    ('a', ['a'], ['#a.1#']),
    ('a.txt', ['a.txt'], ['#a.txt.1#']),
    ('a.txt', ['a'], ['a']),
    ('a.txt', ['a.txt', '#a.txt.1#'], ['#a.txt.2#', '#a.txt.1#']),
    ('a.txt', ['a.txt', '#a.txt.2#'], ['#a.txt.1#', '#a.txt.2#']),
])
def test_backup(tmpdir, monkeypatch, name, existing_files, expected):
    monkeypatch.chdir(tmpdir)
    for idx, file in enumerate(existing_files):
        with open(file, 'w') as handle:
            handle.write(str(idx))

    writer = DeferredFileWriter()
    with writer.open(name, 'w') as handle:
        handle.write("new {}".format(name))
    writer.write()

    assert Path(name).is_file()
    with open(name) as file:
        assert file.read() == "new {}".format(name)

    for idx, name in enumerate(expected):
        assert Path(name).is_file()
        with open(name) as file:
            assert file.read() == str(idx)


def test_deferred_writing(tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)

    file_name = Path('my_file.txt')
    writer = DeferredFileWriter()
    assert not file_name.exists()
    with writer.open(file_name, 'w') as file:
        file.write('hello')
    assert not file_name.exists()
    os.chdir('..')
    writer.write()
    os.chdir(str(tmpdir))
    assert file_name.exists()
    with open(file_name) as file:
        assert file.read() == 'hello'
