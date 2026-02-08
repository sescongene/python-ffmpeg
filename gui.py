import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import subprocess
import threading
import os
import re

class FFMpegConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FFmpeg Video Converter")
        self.root.geometry("700x550")
        
        # Internal State
        self.current_process = None
        self.is_converting = False
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # --- FFmpeg Path Section ---
        ffmpeg_frame = ttk.LabelFrame(root, text="Configuration: FFmpeg Location", padding=(10, 5))
        ffmpeg_frame.pack(fill="x", padx=10, pady=5)
        
        self.ffmpeg_path = tk.StringVar(value="ffmpeg") # Default to system path
        self.ffmpeg_entry = ttk.Entry(ffmpeg_frame, textvariable=self.ffmpeg_path)
        self.ffmpeg_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.btn_ffmpeg = ttk.Button(ffmpeg_frame, text="Browse...", command=self.select_ffmpeg_binary)
        self.btn_ffmpeg.pack(side="right")
        
        # --- Input File Section ---
        input_frame = ttk.LabelFrame(root, text="Step 1: Select Input File", padding=(10, 5))
        input_frame.pack(fill="x", padx=10, pady=5)
        
        self.input_path = tk.StringVar()
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_path)
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.btn_input = ttk.Button(input_frame, text="Browse...", command=self.select_input_file)
        self.btn_input.pack(side="right")
        
        # --- Output Configuration Section ---
        output_frame = ttk.LabelFrame(root, text="Step 2: Output Settings", padding=(10, 5))
        output_frame.pack(fill="x", padx=10, pady=5)
        
        # Format Selection
        ttk.Label(output_frame, text="Format:").pack(side="left", padx=(0, 5))
        self.format_var = tk.StringVar(value="mp4")
        self.format_combo = ttk.Combobox(output_frame, textvariable=self.format_var, values=["mp4", "flv", "mkv"], state="readonly", width=10)
        self.format_combo.pack(side="left", padx=(0, 10))
        self.format_combo.bind("<<ComboboxSelected>>", self.update_output_extension)
        
        # Output Path
        self.output_path = tk.StringVar()
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_path)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.btn_output = ttk.Button(output_frame, text="Save As...", command=self.select_output_file)
        self.btn_output.pack(side="right")
        
        # --- Action Section ---
        action_frame = ttk.Frame(root, padding=(10, 5))
        action_frame.pack(fill="x")
        
        self.btn_convert = ttk.Button(action_frame, text="Convert", command=self.start_conversion)
        self.btn_convert.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        self.btn_abort = ttk.Button(action_frame, text="Abort", command=self.abort_conversion, state='disabled')
        self.btn_abort.pack(side="right", expand=True, fill="x", padx=(5, 0))
        
        # --- Progress & Log ---
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(root, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        
        self.log_area = ScrolledText(root, height=10, state='disabled')
        self.log_area.pack(fill="both", expand=True, padx=10, pady=5)

        # Traces for validation
        self.input_path.trace_add("write", self.validate_form)
        self.output_path.trace_add("write", self.validate_form)
        self.ffmpeg_path.trace_add("write", self.validate_form)
        self.format_var.trace_add("write", self.validate_form)
        
        # Initial validation check
        self.validate_form()

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def select_ffmpeg_binary(self):
        filename = filedialog.askopenfilename(title='Select FFmpeg Executable', filetypes=(('Executables', '*.exe'), ('All files', '*.*')))
        if filename:
            self.ffmpeg_path.set(filename)

    def select_input_file(self):
        # Explicitly supported types only
        filetypes = (
            ('Video files', '*.mp4 *.mkv *.avi *.mov *.flv *.wmv *.webm *.ts'),
        )
        filename = filedialog.askopenfilename(title='Open a file', initialdir='/', filetypes=filetypes)
        if filename:
            self.input_path.set(filename)
            self.generate_default_output(filename)

    def update_output_extension(self, event=None):
        current_output = self.output_path.get()
        if current_output:
            base, _ = os.path.splitext(current_output)
            new_ext = self.format_var.get()
            self.output_path.set(f"{base}.{new_ext}")
        elif self.input_path.get():
             self.generate_default_output(self.input_path.get())

    def generate_default_output(self, input_filename):
        name, _ = os.path.splitext(input_filename)
        ext = self.format_var.get()
        self.output_path.set(f"{name}_converted.{ext}")

    def select_output_file(self):
        ext = self.format_var.get()
        filetypes = ((f'{ext.upper()} files', f'*.{ext}'), ('All files', '*.*'))
        filename = filedialog.asksaveasfilename(title='Save as', initialdir='/', filetypes=filetypes, defaultextension=f".{ext}")
        if filename:
            self.output_path.set(filename)

    def check_ffmpeg(self):
        ffmpeg_exe = self.ffmpeg_path.get()
        try:
            subprocess.run([ffmpeg_exe, '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            return True
        except (FileNotFoundError, subprocess.SubprocessError):
            return False

    def start_conversion(self):
        if not self.check_ffmpeg():
             messagebox.showerror("Error", f"FFmpeg not found at '{self.ffmpeg_path.get()}'.\nPlease install FFmpeg or point to the correct executable.")
             return

        input_file = self.input_path.get()
        output_file = self.output_path.get()
        ffmpeg_exe = self.ffmpeg_path.get()
        
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Error", "Please select a valid input file.")
            return

        if not output_file:
            messagebox.showerror("Error", "Please select an output location.")
            return
            
        self.is_converting = True
        self.btn_convert.config(state='disabled')
        self.btn_abort.config(state='normal')
        self.progress_var.set(0)
        self.log_area.config(state='normal')
        self.log_area.delete('1.0', tk.END)
        self.log_area.config(state='disabled')
        self.log(f"Starting conversion to {self.format_var.get()}...")
        
        thread = threading.Thread(target=self.run_ffmpeg, args=(ffmpeg_exe, input_file, output_file))
        thread.daemon = True
        thread.start()

    def abort_conversion(self):
        if self.current_process and self.is_converting:
            self.log("Aborting conversion...")
            self.current_process.terminate() # Send SIGTERM
            self.is_converting = False

    def run_ffmpeg(self, ffmpeg_exe, input_file, output_file):
        # Select codec based on container/format if needed, but libx264/aac is generally safe for mp4/mkv/flv
        # specific container tweaks can be added here
        
        cmd = [
            ffmpeg_exe, '-y',
            '-i', input_file,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            output_file
        ]
        
        try:
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0 
            )

            total_duration = None
            duration_regex = re.compile(r"Duration: (\d{2}):(\d{2}):(\d{2}).(\d{2})")
            time_regex = re.compile(r"time=(\d{2}):(\d{2}):(\d{2}).(\d{2})")

            while True:
                # If aborted externally
                if not self.is_converting:
                     break

                line = self.current_process.stderr.readline()
                if not line and self.current_process.poll() is not None:
                    break
                
                if line:
                    if total_duration is None:
                        d_match = duration_regex.search(line)
                        if d_match:
                            h, m, s, ms = map(int, d_match.groups())
                            total_duration = h * 3600 + m * 60 + s + ms / 100
                            self.root.after(0, self.log, f"Total duration: {total_duration:.2f}s")
                    
                    t_match = time_regex.search(line)
                    if t_match and total_duration:
                        h, m, s, ms = map(int, t_match.groups())
                        current_time = h * 3600 + m * 60 + s + ms / 100
                        percent = (current_time / total_duration) * 100
                        self.root.after(0, self.progress_var.set, percent)

            # Check if finished naturally or aborted
            if self.is_converting:
                if self.current_process.returncode == 0:
                    self.root.after(0, self.conversion_complete, True)
                else:
                    self.root.after(0, self.conversion_complete, False)
            else:
                 self.root.after(0, self.log, "Conversion aborted by user.")
                 self.root.after(0, self.reset_ui)

        except Exception as e:
            self.root.after(0, self.log, f"Error: {str(e)}")
            self.root.after(0, self.conversion_complete, False)

    def conversion_complete(self, success):
        self.is_converting = False
        self.reset_ui()
        if success:
            self.progress_var.set(100)
            self.log("Conversion successful!")
            messagebox.showinfo("Success", "Video conversion completed successfully.")
        else:
            self.log("Conversion failed.")
            messagebox.showerror("Error", "Video conversion failed. Check logs.")

    def reset_ui(self):
        self.is_converting = False
        self.btn_abort.config(state='disabled')
        self.current_process = None
        self.validate_form()

    def validate_form(self, *args):
        # Do not re-enable if converting
        if self.is_converting:
            return

        # 1. Check if fields are filled
        if not self.input_path.get() or not self.output_path.get() or not self.ffmpeg_path.get():
            self.btn_convert.config(state='disabled')
            return

        # 2. Check extensions
        try:
            input_ext = os.path.splitext(self.input_path.get())[1].lower().lstrip('.')
            target_fmt = self.format_var.get().lower()
            
            if input_ext == target_fmt:
                self.btn_convert.config(state='disabled')
                return
        except Exception:
            pass # Handle potential join/split errors gracefully

        self.btn_convert.config(state='normal')

if __name__ == "__main__":
    root = tk.Tk()
    app = FFMpegConverterApp(root)
    root.mainloop()
