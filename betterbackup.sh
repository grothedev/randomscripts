#!/bin/bash

#a simple backup script that doesn't require to write to network address

if [[ $# -lt 2 ]]; then
    echo 'provide source and destination'
fi


LOGF=/var/log/betterbackup.log
src_path=${1}
dest_path=${2}
if [[ ${3} ]]; then
    rsargs="--exclude-from=${HOME}/.config/rsync-exclude.txt ${3}"
else
    rsargs="--exclude-from=${HOME}/.config/rsync-exclude.txt "
fi

CMD="rsync -av ${rsargs} --progress --update --protect-args -e ssh --log-file=${LOGF} ${src_path} ${dest_path}"
echo "running '${CMD}' in 3 seconds"
sleep 1
echo "2 seconds"
sleep 1
echo "1 second"
sleep 1

d=`date +%Y%m%d_%H%M%S`
echo "starting backup at ${d}" >> ${LOGF}
${CMD}
d=`date +%Y%m%d_%H%M%S`
echo "backup complete at ${d}"
