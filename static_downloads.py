#!/usr/bin/env python3
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
import requests
import hashlib
import os
from pathlib import Path
import json

from misc_aptly_tool_util import download

SCRIPT_DIR = Path.cwd()
DEB_DIR = Path('debs')
CONF_FILE = Path('confs', 'static-urls.json')


def get_new(verbose=False):
    """Download all new .deb packages"""
    def report(message, indent=0):
        if verbose:
            print(("    " * indent) + str(message))
    with open(CONF_FILE, 'r') as package_url_json:
        report('Loading configuration from package_urls.json')
        packages = json.load(package_url_json)
    report("Loaded configuration", 1)
    for package_name in packages:
        report(f'Working on package {package_name}')
        package = DEB_DIR.joinpath(package_name+'.deb')
        url = packages[package_name]['url']
        download(url, package)


if __name__ == '__main__':
    print("Miscellaneous Aptly Tools Copyright (C) 2021 Eli Array Minkoff\n" +
          "This program comes with ABSOLUTELY NO WARRANTY; " +
          "This is free software, and you are welcome to redistribute" +
          "it under certain conditions; for details, " +
          "see the GNU General Public Licence version 3, " +
          "available in the LICENCE file that should have come with this.")
    get_new(verbose=True)
