#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Download FFmpeg (Linux version)
mkdir -p ffmpeg_bin
curl -L https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz | tar xJ -C ffmpeg_bin --strip-components=1
