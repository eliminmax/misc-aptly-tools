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
import re
import json
from pathlib import Path

from misc_aptly_tool_util import eprint
from misc_aptly_tool_util import download
from misc_aptly_tool_util import DEB_DIR


# Declare Constants
CONF_FILE = Path('confs', 'gh-repos.json')
# Pattern for Github API calls
API_TEMPLATE = "https://api.github.com/repos/{}/releases/latest"
# This regex is not exhaustive, but it's a good sanity check
REPO_NAME_REGEX = re.compile('^[a-zA-Z0-9_\\-\\.]+/[a-zA-Z0-9\\-_\\.]+$')


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
        repo: the name of the Github repository (e.g. 'sharkdp/fd'
    Returns:
        A dictionary with the relevant information extracted from the reply
        ['version']: (string) the version name for the release
        ['dl']: a list of 2-long tuples, each of which has the filename, and
        the download URL

    Raises:
        GHAPIError:
            if the API call returns an error code

    """
    api_call = requests.get(API_TEMPLATE.format(repo))
    # Make sure that the API call was successful
    if not api_call.ok:
        raise GHAPIError('Error with Github API call\n' +
                         'HTTP status code: {}\n'.format(api_call.status_code)
                         + 'HTTP reason: {}'.format(api_call.reason))
    # get a dict from the api call output
    api_json = api_call.json()
    # get the release name and all downloadable assets into a dict to return
    parsed_info = {}
    parsed_info['version'] = api_json['name']
    dl_key = 'browser_download_url'
    parsed_info['dl'] = [(i['name'], i[dl_key]) for i in api_json['assets']]
    return parsed_info


def check_pattern(pattern_string, version_name, file_name):
    """Check if a downloadable file name matches a pattern string
    Args:
        pattern_string: a string with the filename, with {VERSION}
            in place of the version name
        version_name: the release version name/number
        file_name: the name of the downloadable to check
    Returns:
        bool: True if the pattern string matches the given filename,
            False otherwise
    """
    expected_file_name = pattern_string.format(VERSION=version_name)
    return expected_file_name == file_name


def get_pattern_match(pattern_string, release_info, version_regex):
    """Get the url for the download that matches a pattern
    Args:
        pattern_string: str - pattern string to check
        release_info: dict - output of get_latest_release_info
        version_regex: str - regex pattern to get the part of the version
                                in the .deb package name
        Returns:
        str - the URL of the download
    Raises:
        UnmatchedPatternError if no match exists
    """
    version = re.search(version_regex, release_info['version']).group(1)
    for dl in release_info['dl']:
        if check_pattern(pattern_string, version, dl[0]):
            return dl
    else:
        # Will run if no match found
        raise UnmatchedPatternError(f"no match for pattern {pattern_string}")


def get_new(verbose=False):
    """Download all new .deb packages"""
    def report(message, indent=0):
        if verbose:
            print(("    " * indent) + str(message))
    report("Loading configuration from gh-repos.json")
    with open(CONF_FILE, 'r') as repo_conf_file:
        repo_conf = json.load(repo_conf_file)
    report("Loaded configuration", 1)
    for repo in repo_conf:
        report(f"Working on repository {repo}")
        # throw an error if it doesn't match the regex for github repos
        try:
            if not REPO_NAME_REGEX.match(repo):
                raise BadRepoNameError('Bad Github Repo: ' + repo)
        except BadRepoNameError as error:
            eprint(error)
            continue
        version_regex = repo_conf[repo]['regex']
        patterns = repo_conf[repo]['patterns']
        if 'versions' not in repo_conf[repo]:
            repo_conf[repo]['versions'] = []
        existing_versions = repo_conf[repo]['versions']
        report(f"Existing versions: {[v for v in existing_versions]}", 1)
        # load json info
        release_info = get_latest_release_info(repo)
        version = release_info['version']
        report(f"Latest upstream version: {version}", 1)
        # check if version is already known
        if version not in existing_versions:
            report("Latest upstream version is not in existing versions", 1)
            existing_versions.append(version)
            # download all files matching patterns
            for pattern_str in patterns:
                try:
                    dl = get_pattern_match(
                        pattern_str, release_info, version_regex
                    )
                    download(dl[1], DEB_DIR.joinpath(dl[0]))
                except UnmatchedPatternError as error:
                    eprint(error)
                    continue
    # Save updated information to gh-repos.json
    with open(CONF_FILE, 'w') as json_file:
        report("Writing updated info to gh-repos.json")
        json.dump(repo_conf, json_file, indent=4)


if __name__ == "__main__":
    print("Miscellaneous Aptly Tools Copyright (C) 2021 Eli Array Minkoff\n" +
          "This program comes with ABSOLUTELY NO WARRANTY; " +
          "This is free software, and you are welcome to redistribute" +
          "it under certain conditions; for details, " +
          "see the GNU General Public Licence version 3, " +
          "available in the LICENCE file that should have come with this.")
    if not DEB_DIR.is_dir():
        DEB_DIR.mkdir(parents=True)
    get_new(verbose=True)
