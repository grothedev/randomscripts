#!/bin/bash

# Configuration
LOG_FILE="process_monitor.log"
CPU_THRESHOLD=397        # Percentage
MEM_THRESHOLD=15360      # Megabytes
KILL_DELAY=10            # Seconds to wait before killing
CHECK_INTERVAL=5         # Seconds between process checks
MAX_KILL_ATTEMPTS=4      # Maximum normal kill attempts before force kill
MIN_PROCESS_AGE=2        # Minimum process age in seconds to consider
WARN_CPU_DIVISOR=4       # Show warning when CPU exceeds threshold/divisor
WARN_MEM_DIVISOR=4       # Show warning when memory exceeds threshold/divisor

# Critical processes that should never be killed
CRITICAL_PROCESSES="^(systemd|init|sshd|bash|loginctl|dbus-daemon|systemd-logind)$"

# Track multiple offending processes
declare -A offender_attempts

while true; do
    # Get the list of running processes
    processes=$(ps -eo pid,pcpu,rss,comm,etimes --sort=-pcpu | grep -v "PID")

    # Loop through the processes
    while read -r process_info; do
        # Extract all process information in a single awk call
        read -r pid cpu_percent mem_kb name dur < <(echo "$process_info" | awk '{print $1, $2, $3, $4, $5}')

        # Skip if any required field is empty or non-numeric
        if [[ -z "$pid" || -z "$dur" || -z "$cpu_percent" || -z "$mem_kb" ]]; then
            continue
        fi

        # Skip if dur is not a number (e.g., defunct processes)
        if ! [[ "$dur" =~ ^[0-9]+$ ]]; then
            continue
        fi

        # Convert memory to MB
        mem_usage=$((mem_kb / 1024))

        # Skip processes younger than minimum age
        if (( dur < MIN_PROCESS_AGE )); then
            continue
        fi

        # Skip critical processes
        if [[ "$name" =~ $CRITICAL_PROCESSES ]]; then
            continue
        fi

        # Warning for processes exceeding 1/4th of threshold
        if (( $(echo "$cpu_percent > $((CPU_THRESHOLD/WARN_CPU_DIVISOR))" | bc -l) )) || (( mem_usage > $((MEM_THRESHOLD/WARN_MEM_DIVISOR)) )); then
            echo "PROCESS! ${pid}:${name} -- ${cpu_percent}%  ${mem_usage}MB  ${dur}s"
        fi

        # Check if the process exceeds the CPU or memory usage threshold
        if (( $(echo "$cpu_percent > $CPU_THRESHOLD" | bc -l) )) || (( mem_usage > MEM_THRESHOLD )); then
            msg_warn="$(date) - Process $name (PID: $pid) has exceeded the threshold: etime: ${dur}, CPU usage: ${cpu_percent}%, Memory usage: ${mem_usage} MB. Killing in ${KILL_DELAY} seconds"

            echo "$msg_warn"
            echo "$msg_warn" >> "$LOG_FILE"
            notify-send -t 8000 "$msg_warn"

            sleep "$KILL_DELAY"

            # Check if process still exists after sleep
            if ! kill -0 "$pid" 2>/dev/null; then
                echo "Process $pid ($name) has already exited"
                unset "offender_attempts[$pid]"
                continue
            fi

            # Track kill attempts for this specific PID
            if [[ -n "${offender_attempts[$pid]}" ]]; then
                offender_attempts[$pid]=$((offender_attempts[$pid] + 1))
            else
                offender_attempts[$pid]=1
            fi

            # ACTUAL PROCESS KILL IS HERE IF YOU NEED TO MODIFY
            if [[ ${offender_attempts[$pid]} -gt $MAX_KILL_ATTEMPTS ]]; then
                echo "Force kill $pid ($name) - attempt ${offender_attempts[$pid]}"
                kill -9 "$pid" 2>/dev/null
            else
                echo "Kill $pid ($name) - attempt ${offender_attempts[$pid]}"
                kill "$pid" 2>/dev/null
            fi

            # Clean up if process is gone
            if ! kill -0 "$pid" 2>/dev/null; then
                echo "Successfully killed process $pid ($name)"
                unset "offender_attempts[$pid]"
            fi
        fi
    done <<< "$processes"

    # Wait before checking again
    sleep "$CHECK_INTERVAL"
done
