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

SCRIPT_DIR = Path.cwd()
DEB_DIR = Path('debs')
CONF_FILE = Path('confs', 'static-urls.json')


def download_latest(package_name, url, previous_md5, verbose):
    """Download the latest .deb; check it against the existing one
    Args:
        package_name: str - the name of the package
        url: str - the url of the package download
        previous_md5: str - the previous download's md5 digest, empty for
            first download
        verbose: bool - whether or not to print info about what it's doing
    Returns:
        str - the md5 of the new download
    """
    if not DEB_DIR.is_dir():
        DEB_DIR.mkdir(parents=True)
    dl = requests.get(url, allow_redirects=True)
    new_md5 = hashlib.md5(dl.content).hexdigest()
    if not dl.ok:
        raise Exception # TODO: More specific error
    if previous_md5 == new_md5:
        # cuts off here if it's the same digest
        return previous_md5
    with open(DEB_DIR.joinpath(package_name + '.deb'), 'wb') as debfile:
        if(verbose):
            print("        MD5 digest differs,",
                  f"saving new file to ./debs/{package_name}.deb")
        debfile.write(dl.content)
    return new_md5


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
        package = packages[package_name]
        url = package['url']
        previous_md5 = package['md5'] if 'md5' in package else ''
        report(f"Previous download md5 digest: {previous_md5}", 1)
        package['md5'] = download_latest(package_name, url,
                                         previous_md5, verbose)
        report(f"New md5 digest: {package['md5']}", 2)
    with open(CONF_FILE, 'w') as package_url_json:
        json.dump(packages, package_url_json, indent=4)


if __name__ == '__main__':
    print("Miscellaneous Aptly Tools Copyright (C) 2021 Eli Array Minkoff\n" +
          "This program comes with ABSOLUTELY NO WARRANTY; " +
          "This is free software, and you are welcome to redistribute" +
          "it under certain conditions; for details, " +
          "see the GNU General Public Licence version 3, " +
          "available in the LICENCE file that should have come with this.")
    get_new(verbose=True)

