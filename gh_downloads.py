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
import re
import json
from os import remove as del_file

import requests
from pydpkg import Dpkg

from misc_aptly_tool_util import eprint
from misc_aptly_tool_util import download
from misc_aptly_tool_util import DATA_DIR
from misc_aptly_tool_util import CONF_DIR
from misc_aptly_tool_util import DEB_DIR


# Declare Constants
# Configuration files
GH_REPO_CONF = CONF_DIR.joinpath("gh-repos.json")
KNOWN_ASSETS_FILE = DATA_DIR.joinpath("known-gh-assets.json")
# Pattern for Github API calls to check for latest version data
API_TEMPLATE = "https://api.github.com/repos/{}/releases/latest"
# This regex is not exhaustive, but it's a good sanity check
REPO_NAME_REGEX = re.compile("^[a-zA-Z0-9_\\-\\.]+/[a-zA-Z0-9\\-_\\.]+$")


# Custom errors
class BadRepoNameError(ValueError):
    """Raised if the repo name fails the REPO_NAME_REGEX check"""

    pass


class GHAPIError(ValueError):
    """Raised if a Github API call returns an error"""

    pass


class UnmatchedPatternError(ValueError):
    """Raised if none of the downloadable files matched a pattern"""

    pass


def get_latest_release_info(repo):
    """Get and parse the JSON info for the latest Github release for the repo
    Args:
        repo: the name of the Github repository (e.g. 'sharkdp/fd')
    Returns:
        A dictionary with the relevant information extracted from the reply
        ['version']: (string) the version name for the release
        ['assets']: (dict) {'node_id': {'name', 'uri'}} for each asset

    Raises:
        GHAPIError:
            if the API call returns an error code

    """
    api_call = requests.get(API_TEMPLATE.format(repo))
    # Make sure that the API call was successful
    if not api_call.ok:
        raise GHAPIError(
            "Error with Github API call\n"
            + "HTTP status code: {}\n".format(api_call.status_code)
            + "HTTP reason: {}".format(api_call.reason)
        )
    # get a dict from the api call output
    api_json = api_call.json()
    # get the release name and all downloadable assets into a dict to return
    parsed_info = {}
    parsed_info["version"] = api_json["name"]
    parsed_info["assets"] = {
        a["node_id"]: {"name": a["name"], "uri": a["browser_download_url"]}
        for a in api_json["assets"]
    }
    return parsed_info


def get_new(verbose=False):
    """Download all new .deb packages that match configuration"""

    def report(message, indent=0):
        if verbose:
            print(("\t" * indent) + str(message))

    # Load configuration data from CONF_DIR/gh-repos.json
    report(f"Loading configuration from {GH_REPO_CONF}")
    with open(GH_REPO_CONF, "r") as repo_conf_file:
        repo_conf = json.load(repo_conf_file)
    report("Loaded configuration", 1)

    # Load known versions from DATA_DIR/known-gh-assets.json
    report(f"Loading known versions from {KNOWN_ASSETS_FILE}")
    if KNOWN_ASSETS_FILE.is_file():
        with open(KNOWN_ASSETS_FILE, "r") as known_assets_file:
            known_assets = json.load(known_assets_file)
    else:
        report(f"{KNOWN_ASSETS_FILE} does not yet exist. Using empty data")
        known_assets = {}

    for repo in repo_conf:
        package_name = repo_conf[repo]["package"]
        arches = repo_conf[repo]["architectures"]
        report(f"Working on repository {repo}")
        # throw an error if it doesn't match the regex for github repos
        try:
            if not REPO_NAME_REGEX.match(repo):
                raise BadRepoNameError("Bad Github Repo: " + repo)
        except BadRepoNameError as error:
            eprint(error)
            continue
        # ensure associated data exists in known_assets
        if repo not in known_assets:
            known_assets[repo] = {"versions": {}}
        if "versions" not in known_assets[repo]:
            known_assets[repo]["versions"] = {}

        # load existing version data
        existing_versions_data = known_assets[repo]["versions"]
        report(f"Existing versions: {[v for v in existing_versions_data]}", 1)
        # load json info
        release_info = get_latest_release_info(repo)
        version = release_info["version"]
        report(f"Latest upstream version: {version}", 1)
        if version not in existing_versions_data:
            existing_versions_data[version] = {}

        for node_id, asset in release_info["assets"].items():
            if node_id not in existing_versions_data[version]:
                existing_versions_data[version][node_id] = asset
                if asset["name"].endswith(".deb"):
                    report("Loading file: " + asset["name"], 2)
                    save_path = DEB_DIR.joinpath(asset["name"])
                    download(asset["uri"], save_path)
                    deb_headers = Dpkg(save_path).headers
                    if deb_headers["Architecture"] not in arches:
                        del_file(save_path)
                        report("DELETED: arch not in configured arches", 3)
                    elif deb_headers["Package"] != package_name:
                        del_file(save_path)
                        report(
                            "DELETED: package name was "
                            + deb_headers["Package"]
                            + ", not "
                            + package_name,
                            3,
                        )

    # Save updated information to KNOWN_ASSETS_FILE
    with open(KNOWN_ASSETS_FILE, "w") as json_file:
        report(f"Writing updated info to {KNOWN_ASSETS_FILE}.")
        json.dump(existing_versions_data, json_file, indent=4)


def main():
    print(
        "Miscellaneous Aptly Tools Copyright (C) 2021 Eli Array Minkoff\n"
        + "This program comes with ABSOLUTELY NO WARRANTY; "
        + "This is free software, and you are welcome to redistribute "
        + "it under certain conditions; for details, "
        + "see the GNU General Public License version 3, "
        + "available in the LICENSE file that should have come with this."
    )
    if not DEB_DIR.is_dir():
        DEB_DIR.mkdir(parents=True)
    get_new(verbose=True)


if __name__ == "__main__":
    main()
