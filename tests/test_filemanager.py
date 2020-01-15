import os
import pytest
from filemanager import FileManifest, File, is_pathname_valid


def test_add_file_manifest():
    path = '/path/to/file.txt'
    fm = FileManifest()
    assert fm.add_file(path)
    assert len(fm.file_manifest) == 1
    assert fm.file_manifest[0] == path


def test_add_duplicate_manifest():
    path = '/path/to/file.txt'
    fm = FileManifest()
    assert fm.add_file(path)
    assert fm.add_file(path) is False


def test_remove_manifest():
    path = '/path/to/file.txt'
    fm = FileManifest()
    assert fm.add_file(path)
    assert fm.remove_file(path)


def test_remove_non_existent_manifest():
    path = '/path/to/file.txt'
    fm = FileManifest()
    assert fm.remove_file(path) is False
    assert fm.remove_file() is False


def test_creating_manifest(fs):
    path = '/path/to/file.txt'
    fm = FileManifest()
    fm.add_file(path)
    f = File(fm)
    assert f.create_files()
    assert os.path.isdir('/path')
    assert os.path.isdir('/path/to')
    assert os.path.exists('/path/to/file.txt')


def test_path_validation():
    assert is_pathname_valid('') is False
    assert is_pathname_valid('/path/to/file.txt')
    with pytest.raises(ValueError):
        assert is_pathname_valid('\x00') is False
