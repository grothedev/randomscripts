#!/bin/bash

# Disk Health and Performance Report Generator
# Requires: smartmontools, hdparm, sysstat (for iostat)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root (use sudo)${NC}"
   exit 1
fi

# Check for required commands
MISSING_DEPS=()
command -v smartctl >/dev/null 2>&1 || MISSING_DEPS+=("smartmontools")
command -v hdparm >/dev/null 2>&1 || MISSING_DEPS+=("hdparm")
command -v iostat >/dev/null 2>&1 || MISSING_DEPS+=("sysstat")

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo -e "${YELLOW}Warning: Missing dependencies: ${MISSING_DEPS[*]}${NC}"
    echo "Install with: sudo apt install ${MISSING_DEPS[*]}"
    echo "Continuing with limited functionality..."
    echo
fi

# Output file
REPORT_FILE="disk_report_$(date +%Y%m%d_%H%M%S).txt"

# Function to print section header
print_header() {
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${BLUE}$1${NC}"
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Function to get disk type
get_disk_type() {
    local disk=$1
    if [[ $disk == nvme* ]]; then
        echo "NVMe"
    elif cat /sys/block/$disk/queue/rotational 2>/dev/null | grep -q "0"; then
        echo "SSD"
    elif cat /sys/block/$disk/queue/rotational 2>/dev/null | grep -q "1"; then
        echo "HDD"
    else
        echo "Unknown"
    fi
}

# Function to format bytes
format_bytes() {
    local bytes=$1
    if [ $bytes -ge 1099511627776 ]; then
        echo "$(awk "BEGIN {printf \"%.2f TB\", $bytes/1099511627776}")"
    elif [ $bytes -ge 1073741824 ]; then
        echo "$(awk "BEGIN {printf \"%.2f GB\", $bytes/1073741824}")"
    else
        echo "$(awk "BEGIN {printf \"%.2f MB\", $bytes/1048576}")"
    fi
}

# Function to check health status
check_health() {
    local disk=$1
    local dev_path="/dev/$disk"

    echo -e "\n${BOLD}SMART Health Status:${NC}"

    if ! command -v smartctl >/dev/null 2>&1; then
        echo -e "${YELLOW}  smartctl not available - install smartmontools${NC}"
        return
    fi

    # Check if SMART is supported
    if ! smartctl -i $dev_path >/dev/null 2>&1; then
        echo -e "${YELLOW}  SMART not supported or accessible for this device${NC}"
        return
    fi

    # Get health status
    local health_status=$(smartctl -H $dev_path 2>/dev/null | grep "SMART overall-health" || echo "Unknown")
    if echo "$health_status" | grep -q "PASSED"; then
        echo -e "  ${GREEN}✓ PASSED${NC}"
    elif echo "$health_status" | grep -q "FAILED"; then
        echo -e "  ${RED}✗ FAILED - IMMEDIATE BACKUP RECOMMENDED${NC}"
    else
        echo -e "  ${YELLOW}? Unknown${NC}"
    fi

    # Get temperature
    local temp=$(smartctl -A $dev_path 2>/dev/null | grep -i "temperature" | head -1 | awk '{print $10}')
    if [ ! -z "$temp" ]; then
        echo "  Temperature: ${temp}°C"
    fi

    # Get power on hours
    local hours=$(smartctl -A $dev_path 2>/dev/null | grep "Power_On_Hours" | awk '{print $10}')
    if [ ! -z "$hours" ]; then
        local days=$((hours / 24))
        echo "  Power On Time: $hours hours ($days days)"
    fi

    # Get reallocated sectors (bad sectors)
    local reallocated=$(smartctl -A $dev_path 2>/dev/null | grep "Reallocated_Sector" | awk '{print $10}')
    if [ ! -z "$reallocated" ]; then
        if [ $reallocated -eq 0 ]; then
            echo -e "  Reallocated Sectors: ${GREEN}$reallocated${NC}"
        else
            echo -e "  Reallocated Sectors: ${YELLOW}$reallocated (warning)${NC}"
        fi
    fi

    # Get wear leveling for SSDs
    local wear=$(smartctl -A $dev_path 2>/dev/null | grep -i "Wear_Leveling_Count\|Media_Wearout_Indicator" | awk '{print $4, $10}')
    if [ ! -z "$wear" ]; then
        echo "  SSD Wear: $wear"
    fi
}

# Function to check performance
check_performance() {
    local disk=$1
    local dev_path="/dev/$disk"

    echo -e "\n${BOLD}Performance Metrics:${NC}"

    # Current I/O stats with iostat
    if command -v iostat >/dev/null 2>&1; then
        echo -e "\n  Current I/O Statistics:"
        iostat -dx $dev_path 1 2 | tail -1 | awk '{
            printf "    Read: %.2f MB/s  Write: %.2f MB/s\n", $6/1024, $7/1024
            printf "    IOPS: %.0f reads/s, %.0f writes/s\n", $4, $5
            printf "    Utilization: %.1f%%\n", $14
        }'
    fi

    # Read speed test with hdparm
    if command -v hdparm >/dev/null 2>&1; then
        echo -e "\n  Sequential Read Speed Test (hdparm):"
        echo "    Testing... (this may take a few seconds)"
        local hdparm_result=$(hdparm -t $dev_path 2>&1 | grep "Timing")
        echo "    $hdparm_result"

        # Cached read test
        local cached_result=$(hdparm -T $dev_path 2>&1 | grep "Timing")
        echo "    $cached_result"
    fi
}

# Function to get disk info
get_disk_info() {
    local disk=$1
    local dev_path="/dev/$disk"

    echo -e "\n${BOLD}Disk Information:${NC}"

    # Get disk model
    local model=$(smartctl -i $dev_path 2>/dev/null | grep "Device Model\|Model Number" | cut -d: -f2 | xargs || echo "Unknown")
    echo "  Model: $model"

    # Get serial number
    local serial=$(smartctl -i $dev_path 2>/dev/null | grep "Serial Number" | cut -d: -f2 | xargs || echo "Unknown")
    echo "  Serial: $serial"

    # Get firmware version
    local firmware=$(smartctl -i $dev_path 2>/dev/null | grep "Firmware Version" | cut -d: -f2 | xargs || echo "Unknown")
    echo "  Firmware: $firmware"

    # Get capacity
    local size_bytes=$(cat /sys/block/$disk/size 2>/dev/null)
    if [ ! -z "$size_bytes" ]; then
        local size_human=$(format_bytes $((size_bytes * 512)))
        echo "  Capacity: $size_human"
    fi

    # Get disk type
    local dtype=$(get_disk_type $disk)
    echo "  Type: $dtype"
}

# Main execution
echo -e "${BOLD}${GREEN}Disk Health and Performance Report${NC}"
echo "Generated: $(date)"
echo

# Discover all physical disks (excluding loop, ram, and other virtual devices)
DISKS=$(lsblk -dn -o NAME,TYPE | grep "disk" | awk '{print $1}' | grep -v "loop\|ram\|sr")

if [ -z "$DISKS" ]; then
    echo -e "${RED}No physical disks found!${NC}"
    exit 1
fi

echo "Found disks: $DISKS"
echo

# Process each disk
for disk in $DISKS; do
    print_header "Disk: /dev/$disk"

    get_disk_info $disk
    check_health $disk
    check_performance $disk

    echo
done

# Summary
print_header "Summary"
echo -e "\n${BOLD}Total Disks Analyzed: $(echo $DISKS | wc -w)${NC}\n"

# Save to file
echo "Report saved to: $REPORT_FILE"
{
    echo "Disk Health and Performance Report"
    echo "Generated: $(date)"
    echo

    for disk in $DISKS; do
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Disk: /dev/$disk"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        get_disk_info $disk
        check_health $disk
        check_performance $disk
        echo
    done
} > "$REPORT_FILE"

echo -e "${GREEN}Done!${NC}"
