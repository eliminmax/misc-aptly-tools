# misc-aptly-tools

Miscelaneous helpers to download deb files for use with aptly automatically. Just schedule whatever helper scripts you want to run at certain intervals.

**`discord/discord-latest.sh`**: downloads latest discord linux `.deb` build, and copies it to {git-root}/debs/discord.deb
- depends: `curl`

**`minecraft/minecraft-latest.sh`**: downloads latest minecraft linux `.deb` build, and copies it to {git-root}/debs/minecraft.deb
- depends: `curl`

**`github/gh-download`**: reads a list of repositories from {git-root}/github/repos.list, uses the Github API and the **jq** tool to parse the list of downloadable `.deb` files in the latest release, and downloads them all to {git-root}/debs
- depends: `curl`, `jq`, `wget`

TODO:
[ ] automatically import downloaded debs to aptly
[ ] rewrite helpers in python, because it's much nicer than shell scripts
[ ] more intelligently handle github downloads (e.g. filter by architecture, allow download of versions other than latest), do not download if the latest version has already been downloaded
