#!/bin/bash

if [[ -z $1 ]]; then
    echo "in what folder do you want to search for text files to move into a subfolder?"
    exit 0
fi

dst='./textfiles/'
if [[ ${2} ]]; then
    dst=${2}
fi

#check that mime type is text. if so, move to 'text' folder
for f in `find ${1} -maxdepth 1 -type f`; do
    if [[ `file -i ${f} | grep 'text/'` ]]; then
        mv ${f} ${dst}
    fi 
done
