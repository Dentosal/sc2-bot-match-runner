#!/usr/bin/env bash
docker ps | grep sc2_ | awk '{print $1}' | xargs docker kill

docker ps -aq --no-trunc | xargs docker rm

docker image ls|grep "<none>"|awk '{print $3}'|xargs docker image rm
