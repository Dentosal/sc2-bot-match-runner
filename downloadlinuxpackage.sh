#!/usr/bin/env bash
set -e
ARCHIVE_NAME=SC2.4.0.2.zip
ARCHIVE_URL="http://blzdistsc2-a.akamaihd.net/Linux/$ARCHIVE_NAME"
if [ -d StarCraftII ]; then
    echo "StarCraftII Linux binaries already present"
else
    if [ ! -e "$ARCHIVE_NAME" ]; then
        curl -O $ARCHIVE_URL
    fi
    unzip -P iagreetotheeula $ARCHIVE_NAME
    rm $ARCHIVE_NAME
fi
