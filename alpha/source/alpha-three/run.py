import subprocess
import os
import shutil
import sys

BUILD_DIR = "build"

def run_cmd(cmd, cwd=None):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")

def clean():
    if os.path.exists(BUILD_DIR):
        print(f"Removing '{BUILD_DIR}' directory...")
        shutil.rmtree(BUILD_DIR)
    else:
        print(f"No '{BUILD_DIR}' directory to remove.")

def configure_and_build():
    # Create build directory
    os.makedirs(BUILD_DIR, exist_ok=True)

    # Run CMake configure
    run_cmd(["cmake", ".."], cwd=BUILD_DIR)

    # Build the project
    run_cmd(["cmake", "--build", "."], cwd=BUILD_DIR)

    print("Build complete!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--clean":
        clean()
        return

    configure_and_build()

if __name__ == "__main__":
    main()
