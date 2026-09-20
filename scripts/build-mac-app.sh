#!/bin/zsh
set -euo pipefail
root=${0:A:h:h}
bundle="$root/dist/Handoffer.app"
mkdir -p "$bundle/Contents/MacOS"
cp "$root/macos/Info.plist" "$bundle/Contents/Info.plist"
swiftc -parse-as-library "$root/macos/HandofferMenu.swift" -o "$bundle/Contents/MacOS/Handoffer"
echo "$bundle"
