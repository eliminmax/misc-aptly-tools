#!/bin/sh

DIR="$(dirname $0)"
cd "$DIR"

curl -Lo ../debs/discord.deb 'https://discord.com/api/download?platform=linux&format=deb'
