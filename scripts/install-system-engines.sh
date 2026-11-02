#!/bin/sh
set -eu
# Intended for the Docker image or an explicitly administered Debian/Ubuntu host.
# No secrets are required. Package licenses/notices remain installed by apt.
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
 libreoffice-writer libreoffice-calc libreoffice-impress \
 ocrmypdf tesseract-ocr tesseract-ocr-por tesseract-ocr-eng tesseract-ocr-spa \
 ghostscript default-jre-headless fonts-dejavu-core fonts-liberation \
 curl ca-certificates chromium
rm -rf /var/lib/apt/lists/*
sh scripts/install-verapdf.sh /opt
