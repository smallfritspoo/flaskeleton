import os
import errno
import sys
from pathlib import Path
from typing import Dict

# Sadly, Python fails to provide the following magic number for us.
ERROR_INVALID_NAME = 123

'''
Windows-specific error code indicating an invalid pathname.

See Also
----------
https://msdn.microsoft.com/en-us/library/windows/desktop/ms681382%28v=vs.85%29.aspx
    Official listing of all such codes.
'''


def is_pathname_valid(pathname: str) -> bool:
    """
    Checks the validity of the provided path.

    :param str pathname: full path to file including filename
    :return: True if the passed pathname is a valid pathname for the current OS; False otherwise.
    :rtype: bool

    :Example:

    >>> print(str(is_pathname_valid('foo.bar')))
    True
    >>> print(str(is_pathname_valid('\x00')))
    False
    >>> print(str(is_pathname_valid('a' * 256)))
    False
    """
    # If this pathname is either not a string or is but is empty, this pathname
    # is invalid.
    try:
        if not isinstance(pathname, str) or not pathname:
            return False

        # Strip this pathname's Windows-specific drive specifier (e.g., `C:\`)
        # if any. Since Windows prohibits path components from containing `:`
        # characters, failing to strip this `:`-suffixed prefix would
        # erroneously invalidate all valid absolute Windows pathnames.
        _, pathname = os.path.splitdrive(pathname)

        # Directory guaranteed to exist. If the current OS is Windows, this is
        # the drive to which Windows was installed (e.g., the "%HOMEDRIVE%"
        # environment variable); else, the typical root directory.
        root_dirname = os.environ.get('HOMEDRIVE', 'C:') \
            if sys.platform == 'win32' else os.path.sep
        assert os.path.isdir(root_dirname)  # ...Murphy and her ironclad Law

        # Append a path separator to this directory if needed.
        root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep

        # Test whether each path component split from this pathname is valid or
        # not, ignoring non-existent and non-readable path components.
        for pathname_part in pathname.split(os.path.sep):
            try:
                os.lstat(root_dirname + pathname_part)
            # If an OS-specific exception is raised, its error code
            # indicates whether this pathname is valid or not. Unless this
            # is the case, this exception implies an ignorable kernel or
            # filesystem complaint (e.g., path not found or inaccessible).
            #
            # Only the following exceptions indicate invalid pathnames:
            #
            # * Instances of the Windows-specific "WindowsError" class
            #   defining the "winerror" attribute whose value is
            #   "ERROR_INVALID_NAME". Under Windows, "winerror" is more
            #   fine-grained and hence useful than the generic "errno"
            #   attribute. When a too-long pathname is passed, for example,
            #   "errno" is "ENOENT" (i.e., no such file or directory) rather
            #   than "ENAMETOOLONG" (i.e., file name too long).
            # * Instances of the cross-platform "OSError" class defining the
            #   generic "errno" attribute whose value is either:
            #   * Under most POSIX-compatible OSes, "ENAMETOOLONG".
            #   * Under some edge-case OSes (e.g., SunOS, *BSD), "ERANGE".
            except OSError as exc:
                if hasattr(exc, 'winerror'):
                    if exc.winerror == ERROR_INVALID_NAME:
                        return False
                elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                    return False
    # If a "TypeError" exception was raised, it almost certainly has the
    # error message "embedded NUL character" indicating an invalid pathname.
    except TypeError as exc:
        return False
    # If no exception was raised, all path components and hence this
    # pathname itself are valid. (Praise be to the curmudgeonly python.)
    else:
        return True
    # If any other exception was raised, this is an unrelated fatal issue
    # (e.g., a bug). Permit this exception to unwind the call stack.
    #
    # Did we mention this should be shipped with Python already?


class FilePath(object):
    def __init__(self, file_path: str) -> None:
        if is_pathname_valid(file_path) is False or file_path == "":
            raise ValueError('Path must be valid, and not empty')
        else:
            self.path = file_path


class FileContent(object):
    def __init__(self, file_contents: str) -> None:
        self.content = file_contents


class FileManifest(object):
    """
    Manages a list of strings representing paths to files that we want to create.
    """
    def __init__(self):
        self.file_manifest: Dict[str, FileContent] = {}

    def add_to_manifest(self, path: FilePath, content: FileContent) -> bool:
        """
        Adds non duplicate paths to the file manifest list
        :param str path: full path to file including filename.
        :param FileContent content: Contents -- if any, to be written to the file.
        :return: True when the value is added to the manifest, False when not.
        :rtype: bool
        """
        # Path is valid and not already in the list
        self.file_manifest[path.path] = content
        return True

    def remove_from_manifest(self, path: FilePath = None) -> bool:
        """
        Removes the provided path from the file manifest list, provided it exists
        :param FilePath path: full path to file including filename.
        :return: True when the file is removed from the file manifest list. False when not.
        :rtype: bool
        """
        if path is not None:
            try:
                del self.file_manifest[path.path]
                return True
            except KeyError as e:
                return False
        else:
            return False


class File(object):
    """
    Handles the creation and population of files and directories.
    """
    def __init__(self, mainfest: FileManifest):
        self.manifest = mainfest.file_manifest

    def create_and_write_files(self) -> bool:
        """
        Loops through the file manifest and creates the files
        :return: True if no errors creating files, False if any are encountered
        :rtype: bool
        """
        try:
            for path, content in self.manifest.items():
                os.makedirs(os.path.dirname(path), exist_ok=True)
                Path(path).touch()
                self.write_file(path, content.content)
        except Exception as e:
            print(e, e.args)
            return False
        return True

    @staticmethod
    def write_file(file: str, rendered_template: str) -> None:
        with open(file, "w") as f:
            f.write(rendered_template)

