#!/bin/sh
# Replace only the existing game-ideas directory; retain the previous tree.
set -eu
release="$1"
case "$release" in game-ideas-[0-9]*Z) ;; *) echo 'Invalid release name'; exit 1;; esac
case "$release" in *[!a-zA-Z0-9-]*) echo 'Invalid release characters'; exit 1;; esac
root=/var/www/orson-huang-homepage
target="$root/game-ideas"
stage="/var/www/.$release"
backup="/var/www/$release-previous"
archive="/root/game-seeds-releases/$release.tar.gz"
manifest="/root/game-seeds-releases/$release.sha256"
test "$(readlink -f "$root")" = "$root"
test "$(readlink -f "$target")" = "$target"
test -d "$target" && test ! -L "$target"
test ! -e "$stage" && test ! -L "$stage"
test ! -e "$backup" && test ! -L "$backup"
before_home=$(sha256sum "$root/index.html")
# Reject unexpected archive members before extracting the locally built package.
tar -tzf "$archive" | while IFS= read -r name; do
  case "$name" in /*|*..*|*\\*) echo 'Unsafe archive path'; exit 1;; esac
  case "$name" in *.html|*.js|*.css|favicon.svg|media/*.svg|media/*.png|reference/growth-config.json|reference/growth-levels.csv|reference/growth-calculator.mjs) ;; *) echo 'Unexpected archive member'; exit 1;; esac
done
mkdir "$stage"
tar -xzf "$archive" -C "$stage" --no-same-owner
(cd "$stage" && sha256sum -c "$manifest")
find "$stage" -type d -exec chmod 755 {} +
find "$stage" -type f -exec chmod 644 {} +
mv -T "$target" "$backup"
if ! mv -T "$stage" "$target"; then
  mv -T "$backup" "$target"
  echo 'Switch failed; previous version restored'
  exit 1
fi
test "$(sha256sum "$root/index.html")" = "$before_home"
echo "Published $release; previous version retained at $backup; homepage unchanged"
