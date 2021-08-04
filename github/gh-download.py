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

# Declare Constants
SCRIPT_ROOT = Path.cwd()
DEB_DIR = Path('..', 'debs')
# Pattern for Github API calls
API_TEMPLATE = "https://api.github.com/repos/{}/releases/latest"
# Path for patterns
REPO_DL_TEMPLATES = SCRIPT_ROOT.joinpath("gh-repo-patterns")
REPO_VERSION_FILE = SCRIPT_ROOT.joinpath("gh-repo-saved-versions.json")
# This regex is not exhaustive, but it's a good sanity check
REPO_NAME_REGEX = re.compile('^[a-zA-Z0-9_\-\.]+/[a-zA-Z0-9\-_\.]+$')


# Custom errors
class MissingRepoPatternError(OSError):
    """Raised if repo pattern is missing"""
    pass


class BadRepoNameError(ValueError):
    """Raised if the repo name fails the REPO_NAME_REGEX check"""
    pass


class GHRepoError(ValueError):
    """Raised if a Github API call returns an error"""
    pass


class BadPatternError(ValueError):
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
        GHRepoError:
            if the API call returns an error code

    """
    api_call = requests.get(API_TEMPLATE.format(repo))
    # Make sure that the API call was successful
    if not api_call.ok:
        raise GHRepoError('Error with Github API call\n' +
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
        BadPatternError if no match exists
    """
    version = re.search(version_regex, release_info['version']).group(1)
    for dl in release_info['dl']:
        if check_pattern(pattern_string, version, dl[0]):
            return dl
    else:
        # Will run if no match found
        raise BadPatternError(f"no match for pattern {pattern_string}")


def version_exists(repo, version, saved_versions):
    """Check if the version has already been downloaded:
    Args:
        repo: str - the name of the Github repository
        version: str - the version identifier
        saved_versions: dict - the saved versions info from REPO_VERSION_FILE
    """
    if repo in saved_versions.keys():
        if version in saved_versions[repo]:
            return True
        else:
            saved_versions[repo].append(version)
    else:
        saved_versions[repo] = [version]
    return False


def get_new():
    if not DEB_DIR.is_dir():
        DEB_DIR.mkdir(parents=True)
    if REPO_VERSION_FILE.is_file():
        with open(REPO_VERSION_FILE, "r") as json_file:
            save_vers = json.load(json_file)
    else:
        save_vers = {}
    with open("gh-repos.json", 'r') as repo_conf_file:
        repo_conf = json.load(repo_conf_file)
    for repo in repo_conf.keys():
        # throw an error if it doesn't match the regex for github repos
        if not REPO_NAME_REGEX.match(repo):
            raise BadRepoListNameError('Bad Github Repo: ' + repo)
        version_regex = repo_conf[repo]['regex']
        patterns = repo_conf[repo]['patterns']
        # load json info
        release_info = get_latest_release_info(repo)
        version = release_info['version']
        # check if version is already known
        if not version_exists(repo, version, save_vers):
            # download all files matching patterns
            for pattern_str in patterns:
                match = get_pattern_match(
                    pattern_str, release_info, version_regex)
                with open(DEB_DIR.joinpath(match[0]), 'wb') as debfile:
                    debfile.write(
                        requests.get(match[1],allow_redirects=True).content
                    )
    with open(REPO_VERSION_FILE, 'w') as json_file:
        json.dump(save_vers, json_file)


if __name__ == "__main__":
    print("Miscellaneous Aptly Tools Copyright (C) 2021 Eli Array Minkoff\n" +
          "This program comes with ABSOLUTELY NO WARRANTY; " +
          "This is free software, and you are welcome to redistribute" +
          "it under certain conditions; for details, " +
          "see the GNU General Public Licence version 3, " +
          "available in the LICENCE file that should have come with this.")
    get_new()
