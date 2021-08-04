# How to use the Github Helper

The Github Helper can be configured with a list of repositories in a JSON format in the file `github/gh-repos.json`.

Each repo configured should have two elements: 
- `regex`: a python regular expression that can get the portion of the release name used in the downloadable package names in it's first capture group
- `patterns`: an array containing the names of the downloads you want, with the version-specific portion replaced with `{VERSION}`

**Example:**

```json
{
    "sharkdp/bat": {
        "regex": "(\\d+\\.\\d+\\.\\d+)",
        "patterns": [
            "bat_{VERSION}_amd64.deb",
            "bat_{VERSION}_arm64.deb",
            "bat_{VERSION}_armhf.deb",
            "bat_{VERSION}_i686.deb"
        ]    
    },
    "PowerShell/PowerShell": {
        "regex": "(\\d+\\.\\d+\\.\\d+)",
        "patterns": [
            "powershell_{VERSION}-1.debian.10_amd64.deb"
        ]
    }
}
```
**Explanation:**

The releases for [`sharkdp/bat`](https://github.com/sharkdp/bat) are given names like `v0.18.2`, and include downloadable `.deb` packages with names like `bat-musl_0.18.2_amd64.deb`, `bat_0.18.2_armhf.deb`, et cetera. In this configuration, the `bat-musl` packages are not desired, but the `bat` packages are, so the patterns for them are included. Because the '`v`' in the release name is not included in the package names, the regex pattern is used to extract the part that is used in the package name.

With [`PowerShell/PowerShell`](https://github.com/PowerShell/PowerShell) releases, the story is similar, but more complex. It has 6 different `.deb` files, each built for amd64, but for a different Debian or Ubuntu release, so this configuration exclusively grabs the version for Debian 10 ('Buster'). PowerShell release names are an even more complex story than `sharkdp/bat`'s, with names like `v7.1.3 Release of PowerShell`, but the same regex pattern can still be used to capture the desired version info.

When run, it will query the Github API to get the latest release for each repository, and check the release name against previously downloaded releases. If the latest release is not a known release, it downloads the files matching the patterns in the `"patterns"` array, and puts them in the `debs` folder, and adds the release to `github/gh-repo-saved-versions.json` for future reference

# How to use the Static URL Helper:

This helper is meant for software that offers a url to download the latest `.deb` file, and updates the `.deb` file it points to, such as Minecraft and Discord.

When run, `static-url/get-latest.py` loads the configuration information from `static-url/package_urls.json`, and downloads the binary data, and saves it to `debs/{package}.deb` unless its md5 hash digest matches the previous download's md5 hash digest

# Final Note

Currently, there are just two indepentent scripts, and they do not integrate with aptly directly. For now, you need to manually add any new files in the `debs` directory to your aptly repository.
