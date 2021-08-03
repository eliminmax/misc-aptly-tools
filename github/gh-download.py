#!/usr/bin/env python3

import requests
import os
import sys
import re
from pathlib import Path

# Declare Constants
SCRIPT_ROOT = Path().cwd()
DEB_DIR = Path('..', 'debs')
# Template for Github API calls
API_TEMPLATE = "https://api.github.com/repos/{user}/{repo}/releases/latest"
# Path for templates
REPO_DL_TEMPLATES = SCRIPT_ROOT.joinpath("gh-repo-templates")
# This regex is not exhaustive, but it's a good sanity check
REPO_NAME_REGEX = re.compile('^[a-zA-Z0-9_\-\.]+/[a-zA-Z0-9\-_\.]+$')

# Custom errors
class MissingRepoTemplateError(OSError):
    """Raised if repo template is missing"""
    pass

class BadRepoNameError(ValueError):
    """Raised if the repo name fails the REPO_NAME_REGEX check"""
    pass

class GHRepoError(ValueError):
    """Raised if a Github API call returns an error"""
    pass

class BadTemplateError(ValueError):
    """Raised if none of the downloadable files matched a template"""
    pass

def get_latest_release_info(gh_user, gh_repo):
    """Get and parse the JSON info for the latest Github release for the repo
    Args:
        gh_user: the username of the Github repository's owner
        gh_repo: the name of the Github repository
    Returns:
        A dictionary with the relevant information extracted from the reply
        ['version']: (string) the version name for the release
        ['dl']: a list of 2-long tuples, each of which has the filename, and
        the download URL

    Raises:
        GHRepoError:
            if the API call returns an error code

    """
    api_call = requests.get(API_TEMPLATE.format(user=gh_user, repo=gh_repo))
    # Make sure that the API call was successful
    if not api_call.ok:
        raise GHRepoError(
            'Error with Github API call\n' +
            'HTTP status code: {}\n'.format(api_call.status_code) +
            'HTTP reason: {}'.format(api_call.reason)
        )
    # get a dict from the api call output
    api_json = api_call.json()
    # get the release name and all downloadable assets into a dict to return
    parsed_info = {}
    parsed_info['version'] = api_json['name'] 
    dl_key = 'browser_download_url'
    parsed_info['dl'] = [(i['name'], i[dl_key]) for i in api_json['assets']]
    return parsed_info


def check_template(template_string, version_name, file_name):
    """Check if a downloadable file name matches a template string
    Args:
        template_string: a string with the filename, with {VERSION}
            in place of the version name
        version_name: the release version name/number
        file_name: the name of the downloadable to check
    Returns:
        bool: True if the template string matches the given filename,
            False otherwise
    """
    expected_file_name = template_string.format(VERSION=version_name)
    return expected_file_name == file_name

def get_template_match(template_string, release_info, version_regex):
    """Get the url for the download that matches a template
    Args:
        template_string: str - template string to check
        release_info: dict - output of get_latest_release_info
        version_regex: str - regex pattern to get the part of the version
                                in the .deb package name
        Returns:
        str - the URL of the download
    Raises:
        BadTemplateError if no match exists
    """
    version = re.search(version_regex, release_info['version']).group(1)
    for dl in release_info['dl']:
        if check_template(template_string, version, dl[0]):
            return dl
    else:
        # Will run if no match found
        raise BadTemplateError(f"no match for template {template_string}")


if __name__ == "__main__":
    if not DEB_DIR.is_dir():
        DEB_DIR.mkdir(parents=True)
    with open(SCRIPT_ROOT.joinpath("gh-repos.list"), 'r') as repo_list:
        for entry in repo_list.readlines():
            repo = entry.strip()
            if repo:
                if repo[0] == '#':
                    # skip to next item if it's a comment:
                    continue
                # throw an error if it doesn't match the regex for github repos:
                if not REPO_NAME_REGEX.match(repo):
                    raise BadRepoListNameError('Bad Github Repo: ' + repo )
                # get the user/repo info
                gh_user, gh_repo = repo.split('/')
                # load the templates for the repo
                template_path = REPO_DL_TEMPLATES.joinpath(gh_user, gh_repo)
                if Path.is_file(template_path):
                    with open(template_path, 'r') as tf:
                        lines = [l.strip() for l in tf.readlines()]
                        version_regex = lines[0]
                        templates = lines[1:]
                    release_info = get_latest_release_info(gh_user, gh_repo)
                    for template_str in templates:
                        match = get_template_match(template_str,
                                                   release_info,
                                                   version_regex)
                        with open(DEB_DIR.joinpath(match[0]), 'wb') as debfile:
                           debfile.write(
                               requests.get(
                                   match[1], allow_redirects=True
                               ).content)
                else:
                    raise MissingRepoTemplateError

