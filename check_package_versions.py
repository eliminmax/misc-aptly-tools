#!/usr/bin/env python3

"""Check the versions of packages, remove if unchanged"""

import json
from os import remove as del_file

from pydpkg import Dpkg

from misc_aptly_tool_util import DEB_DIR
from misc_aptly_tool_util import eprint
from misc_aptly_tool_util import SCRIPT_DIR


def check_deb_file_versions():
    """Check metadata for all packages in DEB_DIR against existing versions
    """
    # If ./info/existing.json exists, load it in.
    EXISTING_DEBS_FILE = SCRIPT_DIR.joinpath("info", "existing.json")
    if EXISTING_DEBS_FILE.exists():
        with open(EXISTING_DEBS_FILE) as f:
            try:
                existing_deb_info = json.load(f)
            except json.decoder.JSONDecodeError as err:
                eprint("Error parsing JSON from ./info/existing.json:", err)
                existing_deb_info = list()
        # If loaded
        if not type(existing_deb_info) == list:
            eprint("./info/existing.json was valid JSON,",
                   "but was not imported as a list.",
                   "Creating an empty list to use")
            del existing_deb_info
            existing_deb_info = list()
    else:
        existing_deb_info = list()
    # Iterate over files in DEB_DIR
    for deb_file in DEB_DIR.glob("*.deb"):
        deb_headers = Dpkg(deb_file).headers
        deb_info = {
            "Package": deb_headers["Package"],
            "Version": deb_headers["Version"],
            "Architecture": deb_headers["Architecture"],
        }
    # If this already exists, delete it, otherwise, add it to known versions
        if deb_info in existing_deb_info:
            del_file(deb_file)
        else:
            existing_deb_info.append(deb_info)

    # Save new version of EXISTING_DEBS_FILE
    with open(EXISTING_DEBS_FILE, 'w') as f:
        json.dump(existing_deb_info, EXISTING_DEBS_FILE)


# if called directly, run check_deb_file_versions()
if __name__ == '__main__':
    check_deb_file_versions()
