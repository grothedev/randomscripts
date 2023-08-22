#!/bin/bash

#this script will take a random line from a random file from a given list of files, and then make a desktop notification (via notify-send) presenting that line along with some of the surrounding lines
#its intended purpose is to run periodically to remind a potential human user to do things
#Author: Thomas Grothe 2023/08/20


files=(~/do) #files from which to draw
#dirs=(~/doc/dev/)

#TODO add the dirs
#for d in ${dirs}; do
#	for f in `find ${d}`; do 
#		if `file ${f} | grep "ASCII text\|Unicode text\|UTF-8 text"`; then
#			files+=(${f})
#		fi	
#	done
#done
#echo ${files[*]}

if [[ $DISPLAY ]]; then 
	notify-send "$(grep "`cat ~/do | grep -v '^$' | shuf -n 1`" -C 2 ~/do | grep -v '^$')" -t 3000
else
	echo "$(grep "`cat ~/do | grep -v '^$' | shuf -n 1`" -C 2 ~/do | grep -v '^$')"
fi
