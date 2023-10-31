#!/bin/bash
#security camera companion script
#move recent images into a folder so they aren't deleted

if [[ $1 ]]; then
	n=${1}
else
	n=40
fi

mv `ls -rt *png | tail -n ${n}` save/
chmod a-w save/*png
#chmod a-w `ls -tr *png  | tail -n ${n}`

