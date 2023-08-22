#!/bin/bash

file="/home/thomas/dev/localutilservice/localutil_webserver.py"

mtime=`stat -c %Y ${file}`
while [[ true ]]; do 
	while [[ $mtime == `stat -c %Y ${file}` ]]; do
		echo "still same modification time"
		sleep 2
		mtime=`stat -c %Y ${file}`
		echo "updated mtime ${mtime}"
	done
	echo "mtime was different. doing thing."
	thingtodo
done

function thingtodo () {
	kill `pgrep -f localutil`
}
