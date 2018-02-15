#!/usr/bin/env bash
docker ps | grep sc2_repo | awk '{print $1}' | xargs docker kill
