import os
import shutil
import subprocess
import glob
import sys

# Define directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(BASE_DIR, 'source')
CONVERTED_DIR = os.path.join(BASE_DIR, 'converted')
ARCHIVE_DIR = os.path.join(BASE_DIR, 'archive')

def check_ffmpeg():
    """Check if ffmpeg is installed and available in the system PATH."""
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except FileNotFoundError:
        print("Error: ffmpeg is not installed or not found in PATH.")
        return False
    except subprocess.SubprocessError:
        print("Error: ffmpeg found but returned an error.")
        return False

def convert_files():
    """Convert video files in source directory to mp4 and move original to archive."""
    # Ensure directories exist
    os.makedirs(CONVERTED_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory '{SOURCE_DIR}' does not exist.")
        return

    # Supported video extensions (add more if needed)
    video_extensions = ['*.mkv', '*.avi', '*.mov', '*.flv', '*.wmv', '*.webm', '*.mp4', '*.ts']
    files_to_convert = []

    for ext in video_extensions:
        files_to_convert.extend(glob.glob(os.path.join(SOURCE_DIR, ext)))

    if not files_to_convert:
        print(f"No video files found in '{SOURCE_DIR}'.")
        return

    print(f"Found {len(files_to_convert)} files to convert.")

    for file_path in files_to_convert:
        filename = os.path.basename(file_path)
        name, _ = os.path.splitext(filename)
        output_filename = f"{name}.mp4"
        output_path = os.path.join(CONVERTED_DIR, output_filename)

        print(f"Converting '{filename}' to '{output_filename}'...")

        # ffmpeg command
        # -y to overwrite output file without asking
        # -i input file
        # -c:v libx264 (H.264 video codec, widely compatible)
        # -c:a aac (AAC audio codec)
        # -strict experimental (sometimes needed for older ffmpeg versions with aac, usually fine without now but harmless)
        cmd = [
            'ffmpeg',
            '-y',
            '-i', file_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            output_path
        ]

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE) 
            print(f"Conversion successful: {output_path}")

            # Move original file to archive
            archive_path = os.path.join(ARCHIVE_DIR, filename)
            shutil.move(file_path, archive_path)
            print(f"Archived original file to: {archive_path}")

        except subprocess.CalledProcessError as e:
            print(f"Error converting '{filename}': {e}")
            # Identify error from stderr if possible, but for now just print exception
            if e.stderr:
                 print(f"FFmpeg stderr: {e.stderr.decode('utf-8')}")

if __name__ == "__main__":
    if check_ffmpeg():
        convert_files()
