# File Monitor Script

A Python script that monitors a directory for new files and automatically transfers them to a remote host via SCP.

## Features

- **Real-time monitoring**: Uses filesystem events to detect new files immediately
- **Automatic transfer**: Transfers files via SCP to a remote host
- **Retry logic**: Retries failed transfers with configurable delays
- **Error handling**: Moves files that fail all retry attempts to an error folder
- **File archiving**: Successfully transferred files are moved to a `.sent` folder
- **Configurable**: All settings controlled via configuration file
- **Logging**: Comprehensive logging with configurable levels
- **File stability**: Waits for files to finish being written before transfer

## Prerequisites

- Python 3.6 or higher
- SSH access to the remote host
- SSH key-based authentication (recommended)

## Installation

1. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. Edit the configuration file `config.ini` with your settings:
   ```bash
   nano config.ini
   ```

## Configuration

Edit `config.ini` with your specific settings:

```ini
[transfer]
# Directory to monitor for new files
watch_directory = /home/user/upload

# Remote server settings
remote_host = myserver.com
remote_path = /var/www/uploads
ssh_user = webuser
ssh_key = /home/user/.ssh/id_rsa
ssh_port = 22

# Retry settings
max_retries = 3
retry_delay = 30.0

# File handling settings
file_settle_delay = 2.0

# Connection settings
connect_timeout = 30
transfer_timeout = 300

# Logging settings
log_level = INFO
log_file = /var/log/file_monitor.log
```

### Configuration Options

- **watch_directory**: Local directory to monitor for new files
- **remote_host**: Hostname or IP of the remote server
- **remote_path**: Destination path on the remote server
- **ssh_user**: Username for SSH connection
- **ssh_key**: Path to SSH private key file
- **ssh_port**: SSH port (default: 22)
- **max_retries**: Number of retry attempts for failed transfers
- **retry_delay**: Seconds to wait between retry attempts
- **file_settle_delay**: Seconds to wait after file creation before transfer
- **connect_timeout**: SSH connection timeout in seconds
- **transfer_timeout**: File transfer timeout in seconds
- **log_level**: Logging level (DEBUG, INFO, WARNING, ERROR)
- **log_file**: Path to log file (optional)

## Usage

1. Start the file monitor:
   ```bash
   python3 file_monitor.py -c config.ini
   ```

2. The script will:
   - Monitor the specified directory for new files
   - Wait for files to finish being written
   - Transfer files to the remote host via SCP
   - Move successful transfers to `.sent/` folder
   - Retry failed transfers up to the configured limit
   - Move permanently failed files to `.error/` folder

3. Stop the monitor with `Ctrl+C`

## Directory Structure

The script creates the following subdirectories in the watch directory:

- `.sent/`: Successfully transferred files
- `.error/`: Files that failed all transfer attempts

## Running as a Service

To run the file monitor as a systemd service, create `/etc/systemd/system/file-monitor.service`:

```ini
[Unit]
Description=File Monitor Service
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/scripts
ExecStart=/usr/bin/python3 /path/to/scripts/file_monitor.py -c /path/to/scripts/config.ini
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable and start the service:

```bash
sudo systemctl enable file-monitor.service
sudo systemctl start file-monitor.service
```

## Troubleshooting

1. **Permission denied errors**: Ensure the SSH key has correct permissions (600)
2. **Connection refused**: Check if SSH is running on the remote host and port is correct
3. **Files not being detected**: Verify the watch directory path is correct and accessible
4. **Transfer timeouts**: Increase `transfer_timeout` for large files

## Security Considerations

- Use SSH key-based authentication instead of passwords
- Restrict SSH key permissions to the specific user and commands needed
- Consider using a dedicated user account for file transfers
- Monitor the `.error/` folder for security issues

## Logs

The script logs all activities including:
- File detection events
- Transfer attempts and results
- Error conditions
- Retry attempts

Log level can be adjusted in the configuration file.
