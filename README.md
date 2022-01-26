# misc-aptly-tools

Miscelaneous "helpers" to download deb files for use with aptly automatically. Just schedule whatever helper scripts you want to run at certain intervals.

I made this because I wanted to be able to use `apt update` and `apt upgrade` to update Discord, Minecraft, and [`bat`](https://github.com/sharkdp/bat), and update to the latest PowerShell release without needing to add a Microsoft-run apt repository to my `sources.list`.

**THIS SOFTWARE IS IN AN ALPHA STATE, AND SHOULD NOT BE USED IN ANY PRODUCTION ENVIRONMENT!**

For usage instructions, see Instructions.md
## TODO:

### General: 
* [x] automatically import downloaded .debs to aptly and update the published apt repo
* [x] rewrite helpers in python, because it's much easier to improve/maintain than shell scripts
* [ ] create a command-line configuration editor
* [x] write proper documentation
* [ ] more graceful error handling - *in progress*
### Github:
* [x] use a less hacked-together system than the current one to handle determining which files to download and add to the repository
* [ ] use an even less hacked-together system than the one created for the previous checklist item
