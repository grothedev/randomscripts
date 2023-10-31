#!/bin/bash
#take a bunch of image files and turn them into a video

if [[ ${#} != 2 ]]; then
	echo "provide file pattern and destination filename"
	exit 0
fi
echo $@
echo "THIS IS SCRIPT IS NOT CURRENTLY WORKING"
ffmpeg -framerate 8 -pattern_type glob -i "${1}" "${2}"
