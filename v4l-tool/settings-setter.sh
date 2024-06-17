#!/bin/bash

#this daemon will keep the brightness, contrast, saturation  of the webcam set based on the time of day

#brightness. highest during darkest
b_mx=245
b_mn=145

#contrast. highest during darkest
c_mx=160
c_mn=100

#saturation. constant for now

while [[ true ]]; do
	th=`date +%H`
	tm=`date +%M`
	p=$(((60*${th}+${tm})/1440)) #percent through day

	sleep 15
done
