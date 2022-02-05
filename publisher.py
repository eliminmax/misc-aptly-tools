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
import json
import subprocess
from pathlib import Path

APTLY_COMMAND = '/usr/bin/aptly'
SCRIPT_DIR = Path.cwd()


def _load_conf():
    with open(SCRIPT_DIR.joinpath('confs', 'aptly-config.json'), 'r') as conf:
        aptly_config = json.load(conf)
    return aptly_config


def _publish_new_packages(repo, to_add, pub, dist, gpg_conf, comp):
    gpg_flags = [f"-{flag}={gpg_conf[flag]}" for flag in gpg_conf]

    # check if aptly repo and publish exist or not
    existing_repos = subprocess.check_output(
        [APTLY_COMMAND, 'repo', 'list', '-raw']
    ).decode().strip().splitlines()

    existing_pub_list = subprocess.check_output(
        [APTLY_COMMAND, 'publish', 'list', '-raw']
    ).decode().strip().splitlines()

    if existing_pub_list and len(existing_pub_list):
        existing_pubs = [p.split(' ')[0] for p in existing_pub_list]
    else:
        existing_pubs = []
    # create repo if it does not exist yet
    if repo not in existing_repos:
        subprocess.run(
            [APTLY_COMMAND, 'repo', 'create', f'-component={comp}',
             f'-distribution={dist}', repo],
            check=True
        )
    # add directory to repo
    subprocess.run([APTLY_COMMAND, 'repo', 'add', '-force-replace',
                    '-remove-files', repo, to_add], check=True)

    # publish repo if not already published, otherwise update publish
    if pub not in existing_pubs:
        subprocess.run(
            [APTLY_COMMAND, 'publish', 'repo', '-batch',
             f'-component={comp}', *gpg_flags, repo, pub],
            check=True
        )
    else:
        subprocess.run(
            [APTLY_COMMAND, 'publish', 'update', '-force-overwrite',
             '-batch', *gpg_flags, dist, pub],
            check=True
        )


def publish(deb_dir=Path('debs')):
    """Publish all new packages

    Params:
        deb_dir: pathlib.Path: the directory of debs to add
            defaults to ./debs)
    """
    aptly_config = _load_conf()
    _publish_new_packages(
        aptly_config['repo'],
        str(deb_dir.resolve()),
        aptly_config['publish'],
        aptly_config['distribution'],
        aptly_config['gpg'] if 'gpg' in aptly_config else {},
        aptly_config['component'] if 'component' in aptly_config else 'main'
    )


if __name__ == '__main__':
    publish()
