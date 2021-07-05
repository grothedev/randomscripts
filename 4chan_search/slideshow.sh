#!/bin/bash

if [[ -z $1 ]]; then
    exit 1
fi

f=$1
n=`wc -l ${f} | cut -d' ' -f 1`

while [[ true ]]; do
    i=`shuf -i 0-${n} -n 1`
    url=`sed -n ${i}'p' ${f}`
    ristretto ${url} &
    sleep 30
    killall ristretto 
done
