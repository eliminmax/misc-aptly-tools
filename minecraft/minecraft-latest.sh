#!/bin/sh

DIR="$(dirname $0)"
cd "$DIR"

curl -Lo ../debs/minecraft.deb 'https://launcher.mojang.com/download/Minecraft.deb'
