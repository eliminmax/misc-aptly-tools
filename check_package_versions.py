#!/usr/bin/env python3

"""Check the versions of packages, remove if unchanged. Rename files if needed
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
from os import remove as del_file

from pydpkg import Dpkg

from misc_aptly_tool_util import DEB_DIR
from misc_aptly_tool_util import eprint
from misc_aptly_tool_util import SCRIPT_DIR


def check_deb_file_versions(verbose=False):
    """Check metadata for all packages in DEB_DIR against existing versions"""
    # If ./confs/existing.json exists, load it in.
    EXISTING_DEBS_FILE = SCRIPT_DIR.joinpath("confs", "existing.json")
    if EXISTING_DEBS_FILE.exists():
        with open(EXISTING_DEBS_FILE) as f:
            try:
                existing_deb_info = json.load(f)
            except json.decoder.JSONDecodeError as err:
                if verbose:
                    eprint("Error parsing ./confs/existing.json:", err)
                existing_deb_info = list()
        # If loaded
        if not type(existing_deb_info) == list:
            if verbose:
                eprint(
                    "./info/existing.json was valid JSON,",
                    "but was not imported as a list.",
                    "Creating an empty list to use",
                )
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
        # If this package/version/arch combo already exists, delete new file
        if deb_info in existing_deb_info:
            del_file(deb_file)
        else:
            # rename file to {package}_{version}_{arch}.deb, if needed
            name_in_repo = (
                f'{deb_info["Package"]}_{deb_info["Version"]}_'
                f'{deb_info["Architecture"]}.deb'
            )
            if deb_file.name != name_in_repo:
                if verbose:
                    print(
                        "Package",
                        deb_info["Package"],
                        "renamed from",
                        deb_file.name,
                        "to",
                        name_in_repo,
                    )
                deb_file.rename(deb_file.parent.joinpath(name_in_repo))
            # Add entry in existing_deb_info
            existing_deb_info.append(deb_info)

    # Save new version of EXISTING_DEBS_FILE
    EXISTING_DEBS_FILE.write_text(json.dumps(existing_deb_info))


# if called directly, run check_deb_file_versions()
if __name__ == "__main__":
    check_deb_file_versions(verbose=True)
