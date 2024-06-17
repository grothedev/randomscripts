#!/bin/bash

# Set the logging configuration
log_file="process_monitor.log"

# Set the CPU and memory usage thresholds
cpu_threshold=50  # Percentage
mem_threshold=500  # Megabytes

while true; do
    # Get the list of running processes
    processes=$(ps -eo pid,pcpu,rss,comm --sort=-pcpu | grep -v "^  PID")
#    echo $processes

    # Loop through the processes
    while read -r process_info; do
        echo "PROCESS! "${process_info}
	echo ""
	# Extract the process information
        pid=$(echo "$process_info" | awk '{print $1}')
        name=$(echo "$process_info" | awk '{print $4}')
        cpu_percent=$(echo "$process_info" | awk '{print $2}')
        mem_usage=$(echo "$process_info" | awk '{print $3}')
        mem_usage=$((mem_usage / 1024))  # Convert to Megabytes
        
	# Check if the process exceeds the CPU or memory usage threshold
        if (( $(echo "$cpu_percent > $cpu_threshold" | bc -l) )) || (( mem_usage > mem_threshold )); then
            echo "$(date) - Process '$name' (PID: $pid) has exceeded the threshold: CPU usage: ${cpu_percent}%, Memory usage: ${mem_usage} MB" # >> "$log_file"
        fi
    done <<< "$processes"

    # Wait for 5 seconds before checking again
    sleep 5
done
