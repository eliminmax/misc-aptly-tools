#!/usr/bin/env python3

import requests
import hashlib
import os
from pathlib import Path
import json

SCRIPT_DIR = Path.cwd()
DEB_DIR = Path('..', 'debs')


def download_latest(package_name, url, previous_md5):
    """Download the latest .deb; check it against the existing one
    Args:
        package_name: str - the name of the package
        url: str - the url of the package download
        previous_md5: str - the previous download's md5 digest, empty for
            first download
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
        debfile.write(dl.content)
    return new_md5


def get_new():
    """Download all new .deb packages"""
    with open('package_urls.json', 'r') as package_url_json:
        packages = json.load(package_url_json)
    for package_name in packages.keys():
        package = packages[package_name]
        url = package['url']
        previous_md5 = package['md5'] if 'md5' in package.keys() else ''
        package['md5'] = download_latest(package_name, url, previous_md5)
    with open('package_urls.json', 'w') as package_url_json:
        json.dump(packages, package_url_json, indent=4)


if __name__ == '__main__':
    print("Miscellaneous Aptly Tools Copyright (C) 2021 Eli Array Minkoff\n" +
          "This program comes with ABSOLUTELY NO WARRANTY; " +
          "This is free software, and you are welcome to redistribute" +
          "it under certain conditions; for details, " +
          "see the GNU General Public Licence version 3, " +
          "available in the LICENCE file that should have come with this.")
    get_new()

