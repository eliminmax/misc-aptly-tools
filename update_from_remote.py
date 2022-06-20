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
import gh_downloads
import static_downloads
import publisher
import check_package_versions
from misc_aptly_tool_util import eprint
from misc_aptly_tool_util import DEB_DIR


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
    try:
        gh_downloads.get_new(verbose=True)
    except Exception as e:
        eprint("\n\nError geting latest Github downloads:")
        eprint(e)
    try:
        static_downloads.get_new(verbose=True)
    except Exception as e:
        eprint("\n\nError getting the latest static url downloads:")
        eprint(e)
    try:
        check_package_versions.check_deb_file_versions(verbose=True)
    except Exception as e:
        eprint("\n\nError checking the package versions:")
        eprint(e)
    # if packages are in deb_dir, add them
    if DEB_DIR.glob("*"):
        publisher.publish()


if __name__ == "__main__":
    main()
