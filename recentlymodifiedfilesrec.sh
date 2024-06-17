#!/bin/bash
#this is a faster implementation than the other script (mostrecentrecursively.sh)

d='.'
declare -a exclude #array of files to exclude from results

if [[ $1 ]]; then
    d=$1
    shift
fi

while [[ $1 ]]; do
    exclude+=(${1})
    shift
done

#set up the exclusion options for the find command
find_cmd_excl=""
for s in ${exclude[@]}; do
    find_cmd_excl+=" -not -wholename \"*${s}*\""
done
find_cmd="find ${d} -type f ${find_cmd_excl} -printf '%T@ %p\n' | sort -n | tail -n 10 | cut -f2- -d' '"
echo $find_cmd
ts=`date +%s_%N`
eval $find_cmd
te=`date +%s_%N`

tss=`echo ${ts} | cut -d'_' -f 1`
tsn=`echo ${ts} | cut -d'_' -f 2`
tes=`echo ${te} | cut -d'_' -f 1`
ten=`echo ${te} | cut -d'_' -f 2`
echo "${tss}, ${tsn}, ${tes}, ${ten}"
tst=$((tss*1000000000 + tsn))
tet=$((tes*1000000000 + ten))
dur=$((tet-tst))
echo "duration: ${dur} ns"
