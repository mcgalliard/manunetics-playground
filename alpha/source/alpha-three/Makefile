# Folder for out-of-source build
BUILD_DIR = build

# Default target: configure and build
all: configure build

# Run CMake configure if build directory doesn't exist or CMakeLists.txt changed
configure:
	@if [ ! -d $(BUILD_DIR) ]; then mkdir $(BUILD_DIR); fi
	@cd $(BUILD_DIR) && cmake ..

# Build the project
build:
	@cd $(BUILD_DIR) && cmake --build .

# Clean build directory
clean:
	rm -rf $(BUILD_DIR)

run:
	@./$(BUILD_DIR)/Debug/main.exe

.PHONY: all configure build clean