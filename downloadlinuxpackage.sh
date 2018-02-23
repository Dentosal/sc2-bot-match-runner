#!/usr/bin/env bash
set -e
ARCHIVE_NAME=SC2.4.0.2.zip
ARCHIVE_URL="http://blzdistsc2-a.akamaihd.net/Linux/$ARCHIVE_NAME"
if [ -d StarCraftII ]; then
    echo "StarCraftII Linux binaries already present"
else
    if [ ! -e "$ARCHIVE_NAME" ]; then
        echo "Downloading StarCraft II Linux binaries"
        curl -O $ARCHIVE_URL
    fi
    unzip -P iagreetotheeula $ARCHIVE_NAME
    rm $ARCHIVE_NAME
fi

MAPS_NAME=Ladder2017Season3_Updated
MAPS_FILE=Ladder2017Season3_Updated.zip
MAPS_URL="http://blzdistsc2-a.akamaihd.net/MapPacks/$MAPS_FILE"

if [ -d StarCraftII/Maps/$MAPS_NAME ]; then
    echo "Maps already loaded in StarCraftII/Maps/$MAPS_NAME"
else
    if [ ! -e "$MAPS_FILE" ]; then
        echo "Downloading maps from $MAPS_URL"
        curl -O $MAPS_URL
    fi
    unzip -P iagreetotheeula $MAPS_FILE -d StarCraftII/Maps
    rm $MAPS_FILE
fi
