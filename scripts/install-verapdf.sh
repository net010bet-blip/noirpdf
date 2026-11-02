#!/bin/sh
set -eu
# Official installer, pinned by checksum. Binaries are not included in the ZIP.
parent="${1:-/opt}"
mkdir -p "$parent"
workdir=$(mktemp -d)
trap 'rm -rf "$workdir"' EXIT
curl --fail --location --retry 3 --connect-timeout 20 https://software.verapdf.org/releases/1.30/verapdf-greenfield-1.30.3-installer.zip -o "$workdir/installer.zip"
printf '%s  %s\n' 'b512bf24945503a33fc10738ecffc1f2dccaaf8593a448e94ee9ac86a9559a59' "$workdir/installer.zip" | sha256sum --check --status || { echo 'veraPDF installer changed upstream: checksum verification failed. Review and update the pinned version before installing.' >&2; exit 1; }
python - "$workdir" <<'PY'
import sys,zipfile
from pathlib import Path
p=Path(sys.argv[1])
with zipfile.ZipFile(p/'installer.zip') as z:
    z.extractall(p/'unpacked')
(p/'install.xml').write_text('''<?xml version="1.0" encoding="UTF-8"?><AutomatedInstallation langpack="eng"><com.izforge.izpack.panels.htmlhello.HTMLHelloPanel id="welcome"/><com.izforge.izpack.panels.target.TargetPanel id="target"/><com.izforge.izpack.panels.packs.PacksPanel id="packs"/><com.izforge.izpack.panels.install.InstallPanel id="install"/><com.izforge.izpack.panels.finish.FinishPanel id="finish"/></AutomatedInstallation>''')
PY
java -Duser.home="$parent" -jar "$workdir/unpacked/verapdf-greenfield-1.30.3/verapdf-izpack-installer-1.30.3.jar" "$workdir/install.xml"
chmod -R a+rX "$parent/verapdf"
"$parent/verapdf/verapdf" --version
