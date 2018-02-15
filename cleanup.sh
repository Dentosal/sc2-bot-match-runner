#!/usr/bin/env bash
docker ps | grep sc2_ | awk '{print $1}' | xargs docker kill
