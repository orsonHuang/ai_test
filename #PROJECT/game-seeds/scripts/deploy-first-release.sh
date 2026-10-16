#!/bin/sh
# Initial deployment only. Existing destinations stop this script for review.
set -eu
release="$1"
case "$release" in game-ideas-[0-9]*Z) ;; *) echo 'Invalid release name'; exit 1;; esac
case "$release" in *[!a-zA-Z0-9-]*) echo 'Invalid release characters'; exit 1;; esac
root=/var/www/orson-huang-homepage
target="$root/game-ideas"
stage="/var/www/.$release"
archive="/root/game-seeds-releases/$release.tar.gz"
test "$(readlink -f "$root")" = "$root"
test ! -e "$target" && test ! -L "$target"
test ! -e "$stage" && test ! -L "$stage"
mkdir "$stage"
tar -xzf "$archive" -C "$stage" --no-same-owner
(cd "$stage" && sha256sum -c /root/game-seeds-releases/SHA256SUMS)
find "$stage" -type d -exec chmod 755 {} +
find "$stage" -type f -exec chmod 644 {} +
mv -T "$stage" "$target"
echo "Published $release to $target"
