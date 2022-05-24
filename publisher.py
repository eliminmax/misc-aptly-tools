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

from misc_aptly_tool_util import DEB_DIR
from misc_aptly_tool_util import SCRIPT_DIR

APTLY_COMMAND = "aptly"


def _load_conf():
    with open(SCRIPT_DIR.joinpath("confs", "aptly-config.json"), "r") as conf:
        aptly_config = json.load(conf)
    return aptly_config


def _aptly(*args):
    """call aptly command with given args"""
    return subprocess.check_output([APTLY_COMMAND, *args]).decode().strip()


def _publish_new_packages(repo, to_add, pub, dist, gpg_conf, comp):
    gpg_flags = [f"-{flag}={gpg_conf[flag]}" for flag in gpg_conf]

    # check if aptly repo and publish exist or not
    existing_repos = _aptly("repo", "list", "-raw").splitlines()

    existing_pub_list = _aptly("publish", "list", "-raw").splitlines()

    if existing_pub_list and len(existing_pub_list):
        existing_pubs = [p.split(" ")[0] for p in existing_pub_list]
    else:
        existing_pubs = []
    # create repo if it does not exist yet
    if repo not in existing_repos:
        _aptly(
            "repo",
            "create",
            f"-component={comp}",
            f"-distribution={dist}",
            repo,
        )
    # add directory to repo
    _aptly("repo", "add", "-force-replace", "-remove-files", repo, to_add)

    # publish repo if not already published, otherwise update publish
    if pub not in existing_pubs:
        _aptly(
            "publish",
            "repo",
            "-batch",
            *gpg_flags,
            f"-component={comp}",
            repo,
            pub,
        )
    else:
        _aptly(
            "publish",
            "update",
            "-force-overwrite",
            *gpg_flags,
            "-batch",
            dist,
            pub,
        )


def publish():
    """Publish all new packages"""
    aptly_config = _load_conf()
    _publish_new_packages(
        aptly_config["repo"],
        str(DEB_DIR.resolve()),
        aptly_config["publish"],
        aptly_config["distribution"],
        aptly_config["gpg"] if "gpg" in aptly_config else {},
        aptly_config["component"] if "component" in aptly_config else "main",
    )


if __name__ == "__main__":
    publish()
