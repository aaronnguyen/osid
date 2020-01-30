#!/usr/bin/env bash
mkdir -p logs
printf "[DuplicatorSettings]
ImagePath = /data
Host = 0.0.0.0
SocketPort = 80
Logs = /usr/src/app/logs
SkeletonLocation = /usr/src/app/www/skeleton.min.css
" > system/server.ini
cat system/balena.id >> system/server.ini
