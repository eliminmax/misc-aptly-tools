"""
This script is a part of Miscellaneous Aptly Tools
    Copyright (C) 2021 Eli Array Minkoff

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from sys import stderr
from os import environ
from pathlib import Path
import requests

SCRIPT_DIR = Path.cwd()
# TODO: allow user to specify directories, rather than this
DEB_DIR = SCRIPT_DIR.joinpath('debs')
CONF_DIR = SCRIPT_DIR.joinpath('confs')
DATA_DIR = SCRIPT_DIR.joinpath('data')


def eprint(*args):
    """Print *args to STDERR"""
    print(*args, file=stderr)


def download(uri, destination):
    """download file from uri to destination, without exhausting memory"""
    with requests.get(uri, stream=True, allow_redirects=True) as r:
        r.raise_for_status()
        with open(destination, 'wb') as f:
            for segment in r.iter_content(4096):
                if segment:
                    f.write(segment)
