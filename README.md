# FFmpeg Converter Project

A Python-based video conversion utility supporting both batch processing (CLI) and single-file processing (GUI).

## Requirements
- Python 3.x
- FFmpeg (Must be installed and added to PATH, or selected manually in GUI)

## Tools

### 1. Command Line Interface (`convert.py`)
Intended for batch processing multiple files.

**How to use:**
1. Place source video files in the `source/` directory.
2. Run the script:
   ```bash
   python convert.py
   ```
3. **Features**:
   - Converts all supported videos (`.mp4`, `.mkv`, `.avi`, `.ts`, etc.) to `.mp4`.
   - Output files are saved in `converted/`.
   - Original files are moved to `archive/` after successful conversion.

### 2. Graphical User Interface (`gui.py`)
Intended for single-file processing with more control.

**How to use:**
1. Run the GUI:
   ```bash
   python gui.py
   ```
2. **Features**:
   - **Format Selection**: Choose specifically between `.mp4`, `.flv`, and `.mkv`.
   - **FFmpeg Override**: Manually select the `ffmpeg.exe` binary if it's not in your system PATH.
   - **Validation**: Prevents conversion if input/output formats are the same or fields are missing.
   - **Progress Tracking**: Visual progress bar showing real-time conversion status.
   - **Abort**: Ability to stop a running conversion.

## Directory Structure
- `source/`: Drop input files here for CLI batch processing.
- `converted/`: Output folder for CLI batch processing.
- `archive/`: Storage for original files after CLI processing.
