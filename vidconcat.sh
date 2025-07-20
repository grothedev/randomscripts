#!/bin/bash
#this script will concatenate videos listed in file vids.txt in this folder into one video
#TODO generate the list automatically

function printHelp() {
	echo "this program will concatenate a number of video files, as specified in a file vids.txt, into one. no arguments required. an mp4 file will be generated with a unique filename."
	echo "in this directory must be a file name vids.txt which contains a list of the video filenames to be concated, where each line is like so: "
	echo "        file \'path/to/file.whatever\'"
	echo "options: "
	echo "  -h: display help"
	echo "  -f [format]: filetype output"
}

if [ ! -f ./vids.txt ]; then
	printHelp
	exit 0
fi

d=`date +%s`
ffmpeg -f concat -safe 0 -i vids.txt -c copy vids-concated-${d}.mp4
#ffmpeg -i video1.mp4 -i video2.mp4 -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0[v]" -map "[v]" output.mp4
