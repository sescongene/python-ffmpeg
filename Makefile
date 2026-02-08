.PHONY: build clean

build:
	@echo "Building standalone executable..."
	python -m PyInstaller --noconfirm --onefile --windowed --name "VideoConverter" gui.py
	@echo "Build complete. Executable is in dist/VideoConverter.exe"

clean:
	@echo "Cleaning up build artifacts..."
	rm -rf build dist *.spec
	@echo "Clean complete."
