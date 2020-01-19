import os
import pytest
import random
import string
from filemanager import (
    File,
    FileManifest,
    FileContent,
    FilePath,
    is_pathname_valid
)

FILE_PATH = '/path/to/file.txt'
FILE_CONTENT = "Some\ncontent\nfor\nfiles"


def test_file_path_creation():
    path = FilePath(FILE_PATH)
    assert path.path == FILE_PATH


def test_file_content_creation():
    content = FileContent(FILE_CONTENT)
    assert content.content == FILE_CONTENT


def test_add_file_manifest():
    fp, fc = FilePath(FILE_PATH), FileContent(FILE_CONTENT)
    fm = FileManifest()
    assert fm.add_to_manifest(fp, fc)
    assert len(fm.file_manifest) == 1
    assert fm.file_manifest[FILE_PATH].content == FILE_CONTENT


def test_add_duplicate_manifest():
    content = ''.join(random.choice(string.ascii_letters) for x in range(4))
    fm = FileManifest()
    fc = FileContent(content)
    fc1 = FileContent(FILE_CONTENT)
    fp = FilePath(FILE_PATH)
    assert fm.add_to_manifest(fp, fc1)
    assert fm.file_manifest[fp.path] == fc1
    assert fm.add_to_manifest(fp, fc)
    assert fm.file_manifest[fp.path] == fc


def test_remove_manifest():
    fp, fc = FilePath(FILE_PATH), FileContent(FILE_CONTENT)
    fm = FileManifest()
    assert fm.add_to_manifest(fp, fc)
    assert fm.remove_from_manifest(fp)


def test_remove_non_existent_manifest():
    fp, fc = FilePath(FILE_PATH), FileContent(FILE_CONTENT)
    fm = FileManifest()
    assert fm.remove_from_manifest(fp) is False
    assert fm.remove_from_manifest() is False


def test_creating_manifest(fs):
    fp, fc = FilePath(FILE_PATH), FileContent(FILE_CONTENT)
    fm = FileManifest()
    fm.add_to_manifest(fp, fc)
    f = File(fm)
    assert f.create_and_write_files()
    assert os.path.isdir('/path')
    assert os.path.isdir('/path/to')
    assert os.path.exists('/path/to/file.txt')
    with open(fp.path, 'r') as content_file:
        content = content_file.read()
    assert content == FILE_CONTENT


def test_path_validation():
    assert is_pathname_valid('') is False
    assert is_pathname_valid('/path/to/file.txt')
    with pytest.raises(ValueError):
        assert is_pathname_valid('\x00') is False
