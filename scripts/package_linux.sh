#!/usr/bin/env bash
set -euo pipefail
mkdir -p dist/release

tar -czf dist/release/SparkPrivacy-Portable-Linux-x64.tar.gz -C dist SparkPrivacy
BUILD=dist/deb-root
rm -rf "$BUILD"
mkdir -p "$BUILD/DEBIAN" "$BUILD/opt/sparkprivacy" "$BUILD/usr/share/applications" "$BUILD/usr/share/icons/hicolor/512x512/apps" "$BUILD/usr/bin"
cp -a dist/SparkPrivacy/. "$BUILD/opt/sparkprivacy/"
cp assets/sparkprivacy-icon.png "$BUILD/usr/share/icons/hicolor/512x512/apps/sparkprivacy.png"
cat > "$BUILD/DEBIAN/control" <<'DEB'
Package: sparkprivacy
Version: 0.1.0
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Md Najmul Hossain
Depends: libgtk-3-0, libwebkit2gtk-4.1-0
Description: Local-first private AI data protection workbench (unsigned preview)
 Secure on-device sensitive-data scanning, local AI policy gateway,
 optional read-only OpenSSH diagnostics, and assessment reporting.
DEB
cat > "$BUILD/usr/share/applications/sparkprivacy.desktop" <<'DESKTOP'
[Desktop Entry]
Type=Application
Name=SparkPrivacy
Comment=Local-first AI security workbench
Exec=/opt/sparkprivacy/SparkPrivacy
Icon=sparkprivacy
Terminal=false
Categories=Development;Security;Utility;
StartupNotify=true
DESKTOP
ln -s /opt/sparkprivacy/SparkPrivacy "$BUILD/usr/bin/sparkprivacy"
dpkg-deb --build --root-owner-group "$BUILD" dist/release/SparkPrivacy-Linux-Ubuntu-x64.deb
