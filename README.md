# misc-aptly-tools

Miscelaneous "helpers" to download deb files for use with aptly automatically. Just schedule whatever helper scripts you want to run at certain intervals.

I made this because I wanted to be able to use `apt update` and `apt upgrade` to update Discord, Minecraft, and [`bat`](https://github.com/sharkdp/bat), and update to the latest PowerShell release without needing to add a Microsoft-run apt repository to my `sources.list`.

**THIS SOFTWARE IS IN AN ALPHA STATE, AND SHOULD NOT BE USED IN ANY PRODUCTION ENVIRONMENT!**

**`static-url/package_urls.json`:** reads a list of static urls for deb packages, and downloads them, adding them if their md5 sum differs from the most recent one for the software

**`github/gh-download.py`**: reads a list of repositories from {git-root}/githugh-repos.json, uses the Github API and the `json` library to parse the list of downloadable `.deb` files in the latest release, and downloads new files to {git-root}/debs

## TODO:

### General: 
* [x] automatically import downloaded .debs to aptly and update the published apt repo
* [x] rewrite helpers in python, because it's much easier to improve/maintain than shell scripts
* [ ] create a command-line configuration editor
* [ ] write proper documentation - *in progress*
* [ ] more graceful error handling

### Github:
* [x] use a less hacked-together system than the current one to handle determining which files to download and add to the repository
