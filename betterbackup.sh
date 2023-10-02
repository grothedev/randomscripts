#!/bin/bash

#a simple backup script that doesn't require to write to network address

if [[ $# != 2; ]]; then
    echo 'provide source and destination'
fi
exit 0

rsync -ahAvz --protect-args -e ssh --update ${src_path} ${dest} ${rsargs} >> /var/log/betterbackup.log
