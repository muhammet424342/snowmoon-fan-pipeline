#!/usr/bin/env sh
# Snowmoon DOG clip: paper texture -> scene -> 192 frames -> out/dog_v1.mp4 (headless).
# Set BLENDER to your Blender 5.2 binary if it is not on PATH.
set -e
cd "$(dirname "$0")"
BLENDER="${BLENDER:-blender}"
python make_paper.py
"$BLENDER" -b -P scene_dog.py -P animate_dog.py -- --render
