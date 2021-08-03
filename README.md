# misc-aptly-tools

Miscelaneous "helpers" to download deb files for use with aptly automatically. Just schedule whatever helper scripts you want to run at certain intervals.

I made this because I wanted to be able to use `apt update` and `apt upgrade` to update Discord, Minecraft, and [`bat`](https://github.com/sharkdp/bat), and update to the latest PowerShell release without needing to add a Microsoft-run apt repository to my `sources.list`.

**THIS SOFTWARE IS IN A PRE-ALPHA STATE, AND SHOULD NOT BE USED IN ANY PRODUCTION ENVIRONMENT!**

**`discord/discord-latest.sh`**: downloads latest discord linux `.deb` build, and copies it to {git-root}/debs/discord.deb
- depends: `curl`

**`minecraft/minecraft-latest.sh`**: downloads latest minecraft linux `.deb` build, and copies it to {git-root}/debs/minecraft.deb
- depends: `curl`

**`github/gh-download`**: reads a list of repositories from {git-root}/github/repos.list, uses the Github API and the **jq** tool to parse the list of downloadable `.deb` files in the latest release, and downloads them all to {git-root}/debs
- depends: `curl`, `jq`, `wget`

## TODO:

### General: 
* [ ] automatically import downloaded debs to aptly
* [ ] rewrite helpers in python, because it's much easier to improve/maintain than shell scripts - *in progress*

### Github:
* [ ] use a less hacked-together system than the current one to handle determining which files to download and add to the repository
