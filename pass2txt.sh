#!/bin/bash

#this script takes the passwords from the "pass" database (~/.password) and outputs them into a text file
#yes this writes passwords to plaintext so only use if you know what you're doing

passdb=`realpath ~/.password-store/`
outfile="./passwords-in-plaintext.txt"
if [[ $1 ]]; then
	outfile="$1"
fi
echo "reading from "${passdb}
echo "and writing to "${outfile}


for f in `find ${passdb} | grep \.gpg`; do 
	#echo $f >> ${outfile}
	#pass `echo $f | sed 's/\.gpg//g'` >> ${outfile}
	pswd=`gpg --quiet -d ${f} >> ${outfile} `
	echo "${f} : ${pswd}" >> ${outfile}
done

