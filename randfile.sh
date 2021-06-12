#!/bin/bash

#select a random file recursively from the given folder

dir="."
if [[ $1 ]]; then
    dir=$1
fi

#recursively list all files
find ${dir} > /tmp/randfilefind

#get number of files
n=`wc -l /tmp/randfilefind | cut -d' ' -f 1`

#select a random file
i=`shuf -i 0-${n} -n 1`
f=`sed -n ${i}'p' /tmp/randfilefind`

echo "The Chosen File: "${f}

rm /tmp/randfilefind
