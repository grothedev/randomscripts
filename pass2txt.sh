#!/bin/bash

#this script will take the passwords from the "pass" databaes (~/.password) and outputs them into a text file

passdb=`realpath ~/.password-store/`
outfile="./passwords-in-plaintext.txt"
if [[ $1 ]]; then
	outfile="$1"
fi
echo "reading from "${passdb}
echo "and writing to "${outfile}


for f in `find ${passdb} | grep \.gpg`; do 
	echo $f >> ${outfile}
	pass `echo $f | sed 's/\.gpg//g'` >> ${outfile}
	echo "" >> ${outfile}
done

