#!/bin/bash
#this script repeatedly captures images from a video device (e.g. /dev/video0) at regular intervals
#and it compresses images into an .tar.gz after some number and deletes those images
#and it deletes old archives after some number have been made

MAX_SIZE=1073741824 #1G in bytes
TIME_INTERVAL=15 #seconds between taking snapshots
THRESHOLD_ARCHIVE=5760 #number of images after which archiving should be done. 5760 is one day if pics are every 15s
THRESHOLD_REMOVE=30 #number of image archive tarballs after which a handful of the oldest archives will be deleted

while [[ true ]]; do
	d=`date +%Y%m%d_%H%M%S`
	snapshot ${d}.png
	ln -snf ${d}.png current.png
	sleep ${TIME_INTERVAL}
	if [[ `find . -maxdepth 1 -name "*png" | wc -l` -gt ${THRESHOLD_ARCHIVE} ]]; then
	#if [[ `ls *png | wc -l` -gt ${THRESHOLD_ARCHIVE} ]]; then
		echo "time to archive captured images"
		mkdir archive${d}
		mv *png archive${d}/
		tar -czvf archive${d}.tar.gz archive${d}/*
		echo "archive made. images compressed. now deleting source files."
		rm -rf archive${d}
	fi
	if [[ `ls archive* 2&>/dev/null | wc -l` -gt ${THRESHOLD_REMOVE} ]]; then
		echo "time to remove some old archived image sets"
		rm `ls -t . | grep archive | tail -n 5` -rf
	fi
done


#if [ `du . -b | awk '{print $1}'` -gt ${MAX_SIZE} ]; then

