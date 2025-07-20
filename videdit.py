#!/usr/bin/env python3
"""
Video Clip Extractor GUI
A simple GUI application for extracting video clips using ffmpeg
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import threading
from pathlib import Path
import re

class VideoClipperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Clip Extractor")
        self.root.geometry("600x400")
        
        # Variables
        self.input_file = tk.StringVar()
        self.start_time = tk.StringVar(value="00:00:00")
        self.end_time = tk.StringVar(value="00:00:10")
        self.output_dir = tk.StringVar(value=os.getcwd())
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Input file selection
        ttk.Label(main_frame, text="Input Video File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(0, weight=1)
        
        self.file_entry = ttk.Entry(file_frame, textvariable=self.input_file, state="readonly")
        self.file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=1)
        
        # Time inputs
        ttk.Label(main_frame, text="Start Time:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.start_entry = ttk.Entry(main_frame, textvariable=self.start_time, width=15)
        self.start_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text="(HH:MM:SS or seconds)").grid(row=1, column=2, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(main_frame, text="End Time:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.end_entry = ttk.Entry(main_frame, textvariable=self.end_time, width=15)
        self.end_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text="(HH:MM:SS or seconds)").grid(row=2, column=2, sticky=tk.W, padx=(5, 0))
        
        # Output directory
        ttk.Label(main_frame, text="Output Directory:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(0, weight=1)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_dir)
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(output_frame, text="Browse", command=self.browse_output_dir).grid(row=0, column=1)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="5")
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(1, weight=1)
        
        # Quality/encoding options
        ttk.Label(options_frame, text="Quality:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.quality_var = tk.StringVar(value="copy")
        quality_combo = ttk.Combobox(options_frame, textvariable=self.quality_var, width=15)
        quality_combo['values'] = ("copy (fastest)", "high", "medium", "low")
        quality_combo.grid(row=0, column=1, sticky=tk.W)
        
        # Extract button
        self.extract_btn = ttk.Button(main_frame, text="Extract Clip", command=self.extract_clip)
        self.extract_btn.grid(row=5, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status/output text
        text_frame = ttk.LabelFrame(main_frame, text="Output", padding="5")
        text_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        self.output_text = tk.Text(text_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Initial message
        self.log_message("Ready to extract video clips. Select a video file to begin.")
        
    def browse_file(self):
        """Open file dialog to select input video file"""
        filetypes = [
            ("Video files", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.m4v"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=filetypes
        )
        
        if filename:
            self.input_file.set(filename)
            self.log_message(f"Selected input file: {os.path.basename(filename)}")
            
    def browse_output_dir(self):
        """Open directory dialog to select output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)
            
    def validate_time_format(self, time_str):
        """Validate and normalize time format"""
        time_str = time_str.strip()
        
        # If it's just numbers, treat as seconds
        if re.match(r'^\d+(\.\d+)?$', time_str):
            return float(time_str)
            
        # If it's HH:MM:SS format
        if re.match(r'^\d{1,2}:\d{2}:\d{2}(\.\d+)?$', time_str):
            return time_str
            
        # If it's MM:SS format, convert to HH:MM:SS
        if re.match(r'^\d{1,2}:\d{2}(\.\d+)?$', time_str):
            return f"00:{time_str}"
            
        raise ValueError(f"Invalid time format: {time_str}")
        
    def log_message(self, message):
        """Add message to output text widget"""
        self.output_text.insert(tk.END, f"{message}\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
        
    def get_ffmpeg_quality_params(self):
        """Get ffmpeg parameters based on quality setting"""
        quality = self.quality_var.get()
        
        if "copy" in quality:
            return ["-c", "copy"]
        elif "high" in quality:
            return ["-c:v", "libx264", "-crf", "18", "-c:a", "aac", "-b:a", "192k"]
        elif "medium" in quality:
            return ["-c:v", "libx264", "-crf", "23", "-c:a", "aac", "-b:a", "128k"]
        elif "low" in quality:
            return ["-c:v", "libx264", "-crf", "28", "-c:a", "aac", "-b:a", "96k"]
        else:
            return ["-c", "copy"]
            
    def extract_clip(self):
        """Extract video clip using ffmpeg"""
        # Validation
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input video file")
            return
            
        if not os.path.isfile(self.input_file.get()):
            messagebox.showerror("Error", "Input file does not exist")
            return
            
        try:
            start_time = self.validate_time_format(self.start_time.get())
            end_time = self.validate_time_format(self.end_time.get())
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
            
        # Disable extract button and start progress
        self.extract_btn.config(state="disabled")
        self.progress.start()
        
        # Run extraction in separate thread
        thread = threading.Thread(target=self._run_extraction, args=(start_time, end_time))
        thread.daemon = True
        thread.start()
        
    def _run_extraction(self, start_time, end_time):
        """Run ffmpeg extraction in background thread"""
        try:
            # Generate output filename
            input_path = Path(self.input_file.get())
            timestamp = str(int(os.path.getctime(self.input_file.get())))
            output_filename = f"{input_path.stem}_clip_{timestamp}{input_path.suffix}"
            output_path = os.path.join(self.output_dir.get(), output_filename)
            
            # Build ffmpeg command
            cmd = ["ffmpeg", "-i", self.input_file.get()]
            
            # Add start time
            if isinstance(start_time, (int, float)) and start_time > 0:
                cmd.extend(["-ss", str(start_time)])
            elif isinstance(start_time, str) and start_time != "00:00:00":
                cmd.extend(["-ss", start_time])
                
            # Add duration or end time
            if isinstance(end_time, (int, float)) and isinstance(start_time, (int, float)):
                duration = end_time - start_time
                cmd.extend(["-t", str(duration)])
            elif isinstance(end_time, str):
                cmd.extend(["-to", end_time])
                
            # Add quality parameters
            cmd.extend(self.get_ffmpeg_quality_params())
            
            # Add output file
            cmd.append(output_path)
            
            self.log_message(f"Starting extraction...")
            self.log_message(f"Command: {' '.join(cmd)}")
            
            # Run ffmpeg
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.output_dir.get()
            )
            
            # Handle results
            if process.returncode == 0:
                self.log_message(f"✓ Successfully extracted clip to: {output_filename}")
                self.log_message(f"Output file size: {self._get_file_size(output_path)}")
            else:
                self.log_message(f"✗ Error during extraction:")
                self.log_message(process.stderr)
                
        except Exception as e:
            self.log_message(f"✗ Exception occurred: {str(e)}")
            
        finally:
            # Re-enable button and stop progress
            self.root.after(0, self._extraction_finished)
            
    def _extraction_finished(self):
        """Called when extraction is finished"""
        self.progress.stop()
        self.extract_btn.config(state="normal")
        
    def _get_file_size(self, filepath):
        """Get human-readable file size"""
        try:
            size = os.path.getsize(filepath)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "Unknown"

def main():
    # Check if ffmpeg is available
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        messagebox.showerror("Error", "ffmpeg not found. Please install ffmpeg and ensure it's in your PATH.")
        return
        
    root = tk.Tk()
    app = VideoClipperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()