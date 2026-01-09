#!/bin/bash

# Set the logging configuration
log_file="process_monitor.log"

# Set the CPU and memory usage thresholds
cpu_threshold=396  # Percentage
mem_threshold=15360  # Megabytes
offender=-1
kill_attempts=0

while true; do
    # Get the list of running processes
    processes=$(ps -eo pid,pcpu,rss,comm,etimes --sort=-pcpu | grep -v "PID")
#    echo $processes

    # Loop through the processes
    while read -r process_info; do
	# Extract the process information
        pid=$(echo "$process_info" | awk '{print $1}')
        name=$(echo "$process_info" | awk '{print $4}')
        dur=$(echo "$process_info" | awk '{print $5}')
        cpu_percent=$(echo "$process_info" | awk '{print $2}')
        mem_usage=$(echo "$process_info" | awk '{print $3}')
        mem_usage=$((mem_usage / 1024))  # Convert to Megabytes

        #if (( ${dur} < 2 )); then continue; fi
        if (( dur < 2 )); then continue; fi
        
        # this is just checking if the process exceeds 1/4th of threshold
        if (( $(echo "$cpu_percent > $((cpu_threshold/4))" | bc -l) )) || (( mem_usage > $((mem_threshold/4)) )); then
            echo "PROCESS! ${pid}:${name} -- ${cpu_percent}%  ${mem_usage}MB  ${dur}s"
        fi 

        # Check if the process exceeds the CPU or memory usage threshold
        if (( $(echo "$cpu_percent > $cpu_threshold" | bc -l) )) || (( mem_usage > mem_threshold )); then
            msg_warn="$(date) - Process $name (PID: $pid) has exceeded the threshold: etime: ${dur}, CPU usage: ${cpu_percent}%, Memory usage: ${mem_usage} MB. Killing in 10 seconds" # >> "$log_file"
            echo ${msg_warn}
            notify-send -t 8000 "$msg_warn"
            sleep 10
            if [[ $pid != $offender ]]; then
                offender=$pid
                #TODO deal with multiple offending processes later
            fi

            # ACTUAL PROCESS KILL IS HERE IF YOU NEED TO MODIFY
            if [[ ${kill_attempts} -gt 4 ]]; then       
                echo "force kill ${pid}"
                sleep 1
                kill_attempts=$((kill_attempts+1))
                kill -9 ${pid}
            else
                echo "kill ${pid}. attempt ${kill_attempts}"
                sleep 1
                kill_attempts=$((kill_attempts+1))
                kill ${pid}
            fi
            sleep 1
            if [[ $(! kill -0 ${pid} 2>/dev/null) ]]; then
                offender=-1
                kill_attempts=0
            fi
        fi
    done <<< "$processes"

    # Wait for 5 seconds before checking again
    sleep 5
done
