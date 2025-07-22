#!/usr/bin/env python3
"""
File Monitor Script
Monitors a directory for new files and transfers them via SCP.
Handles retries and error cases.
"""

import os
import sys
import time
import shutil
import logging
import argparse
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Timer
import configparser

class FileTransferHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config
        self.watch_dir = Path(config['watch_directory'])
        self.sent_dir = self.watch_dir / '.sent'
        self.error_dir = self.watch_dir / '.error'
        self.processing_files = set()
        
        # Create directories if they don't exist
        self.sent_dir.mkdir(exist_ok=True)
        self.error_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        log_level = getattr(logging, self.config.get('log_level', 'INFO').upper())
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        if self.config.get('log_file'):
            logging.basicConfig(
                level=log_level,
                format=log_format,
                handlers=[
                    logging.FileHandler(self.config['log_file']),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        else:
            logging.basicConfig(level=log_level, format=log_format)
            
        self.logger = logging.getLogger(__name__)
        
    def on_created(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        
        # Skip hidden files and our own directories
        if file_path.name.startswith('.'):
            return
            
        self.logger.info(f"New file detected: {file_path}")
        
        # Wait a bit to ensure file is completely written
        delay = float(self.config.get('file_settle_delay', '2.0'))
        Timer(delay, self.process_file, args=[file_path]).start()
        
    def process_file(self, file_path):
        """Process a single file for transfer"""
        if not file_path.exists():
            self.logger.warning(f"File no longer exists: {file_path}")
            return
            
        if str(file_path) in self.processing_files:
            self.logger.debug(f"File already being processed: {file_path}")
            return
            
        self.processing_files.add(str(file_path))
        
        try:
            # Check if file is still being written to
            while not self.is_file_stable(file_path):
                self.logger.debug(f"File still being written, retrying later: {file_path}")
                # Timer(2.0, self.process_file, args=[file_path]).start()
                time.sleep(1)
                
            self.transfer_file_with_retry(file_path)
            
        finally:
            self.processing_files.discard(str(file_path))
            
    def is_file_stable(self, file_path, check_interval=1.0):
        """Check if file size is stable (not being written to)"""
        try:
            size1 = file_path.stat().st_size
            time.sleep(check_interval)
            size2 = file_path.stat().st_size
            return size1 == size2
        except OSError:
            return False
            
    def transfer_file_with_retry(self, file_path):
        """Transfer file with retry logic"""
        max_retries = int(self.config.get('max_retries', '3'))
        retry_delay = float(self.config.get('retry_delay', '30.0'))
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Transferring {file_path} (attempt {attempt + 1}/{max_retries})")
                
                if self.scp_transfer(file_path):
                    self.move_to_sent(file_path)
                    self.logger.info(f"Successfully transferred and archived: {file_path}")
                    return
                else:
                    raise Exception("SCP transfer failed")
                    
            except Exception as e:
                self.logger.error(f"Transfer attempt {attempt + 1} failed for {file_path}: {e}")
                
                if attempt < max_retries - 1:
                    self.logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"All transfer attempts failed for {file_path}, moving to error folder")
                    self.move_to_error(file_path)
                    
    def scp_transfer(self, file_path):
        """Perform SCP transfer"""
        try:
            # Build SCP command
            remote_host = self.config['remote_host']
            remote_path = self.config.get('remote_path', '.')
            ssh_key = self.config.get('ssh_key')
            ssh_user = self.config.get('ssh_user', 'root')
            ssh_port = self.config.get('ssh_port', '22')
            
            # Remote destination
            if remote_path.endswith('/'):
                remote_dest = f"{ssh_user}@{remote_host}:{remote_path}{file_path.name}"
            else:
                remote_dest = f"{ssh_user}@{remote_host}:{remote_path}/{file_path.name}"
            
            # Build command
            cmd = ['scp']
            
            # Add SSH options
            ssh_options = [
                '-o', 'BatchMode=yes',
                '-o', 'StrictHostKeyChecking=no',
                '-o', f'ConnectTimeout={self.config.get("connect_timeout", "30")}',
                '-P', ssh_port
            ]
            
            if ssh_key:
                ssh_options.extend(['-i', ssh_key])
                
            cmd.extend(ssh_options)
            cmd.extend([str(file_path), remote_dest])
            
            self.logger.debug(f"Running command: {' '.join(cmd)}")
            
            # Execute SCP
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=int(self.config.get('transfer_timeout', '300'))
            )
            
            if result.returncode == 0:
                self.logger.debug(f"SCP transfer successful for {file_path}")
                return True
            else:
                self.logger.error(f"SCP failed with return code {result.returncode}")
                self.logger.error(f"STDERR: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"SCP transfer timed out for {file_path}")
            return False
        except Exception as e:
            self.logger.error(f"SCP transfer error for {file_path}: {e}")
            return False
            
    def move_to_sent(self, file_path):
        """Move file to sent directory"""
        try:
            dest_path = self.sent_dir / file_path.name
            # Handle filename conflicts
            counter = 1
            while dest_path.exists():
                name_parts = file_path.stem, counter, file_path.suffix
                dest_path = self.sent_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                counter += 1
                
            shutil.move(str(file_path), str(dest_path))
            self.logger.info(f"File archived to: {dest_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to move file to sent directory: {e}")
            
    def move_to_error(self, file_path):
        """Move file to error directory"""
        try:
            dest_path = self.error_dir / file_path.name
            # Handle filename conflicts
            counter = 1
            while dest_path.exists():
                name_parts = file_path.stem, counter, file_path.suffix
                dest_path = self.error_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                counter += 1
                
            shutil.move(str(file_path), str(dest_path))
            self.logger.info(f"File moved to error directory: {dest_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to move file to error directory: {e}")

def load_config(config_file):
    """Load configuration from file"""
    config = configparser.ConfigParser()
    config.read(config_file)
    
    if 'transfer' not in config:
        raise ValueError("Configuration file must contain a [transfer] section")
        
    return dict(config['transfer'])

def create_sample_config(config_file):
    """Create a sample configuration file"""
    config = configparser.ConfigParser()
    
    config['transfer'] = {
        'watch_directory': '/path/to/watch/directory',
        'remote_host': 'example.com',
        'remote_path': '/remote/destination/path',
        'ssh_user': 'username',
        'ssh_key': '/path/to/ssh/private/key',
        'ssh_port': '22',
        'max_retries': '3',
        'retry_delay': '30.0',
        'file_settle_delay': '2.0',
        'connect_timeout': '30',
        'transfer_timeout': '300',
        'log_level': 'INFO',
        'log_file': '/path/to/logfile.log'
    }
    
    with open(config_file, 'w') as f:
        config.write(f)
        
    print(f"Sample configuration created at: {config_file}")
    print("Please edit the configuration file with your settings before running the script.")

def main():
    parser = argparse.ArgumentParser(description='Monitor directory and transfer files via SCP')
    parser.add_argument('-c', '--config', required=True, help='Configuration file path')
    parser.add_argument('--create-config', action='store_true', 
                       help='Create a sample configuration file')
    
    args = parser.parse_args()
    
    if args.create_config:
        create_sample_config(args.config)
        return
        
    if not os.path.exists(args.config):
        print(f"Configuration file not found: {args.config}")
        print(f"Use --create-config to create a sample configuration file")
        sys.exit(1)
        
    try:
        config = load_config(args.config)
        
        # Validate required settings
        required_settings = ['watch_directory', 'remote_host']
        for setting in required_settings:
            if setting not in config:
                print(f"Required setting missing from config: {setting}")
                sys.exit(1)
                
        watch_dir = Path(config['watch_directory'])
        if not watch_dir.exists():
            print(f"Watch directory does not exist: {watch_dir}")
            sys.exit(1)
            
        # Create handler and observer
        handler = FileTransferHandler(config)
        observer = Observer()
        observer.schedule(handler, str(watch_dir), recursive=False)
        
        # Start monitoring
        observer.start()
        handler.logger.info(f"Started monitoring directory: {watch_dir}")
        handler.logger.info(f"Transferring to: {config['remote_host']}")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            handler.logger.info("Stopping file monitor...")
            observer.stop()
            
        observer.join()
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
