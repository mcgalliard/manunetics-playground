# Minimum required version of CMake
cmake_minimum_required(VERSION 3.10)

# Project name
project(MyProject C)

# Set C standard
set(CMAKE_C_STANDARD 99)

# Set output directory
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/output)

# Include header files
include_directories(${CMAKE_SOURCE_DIR}/includes)

# Get all .c files in source/ folder
file(GLOB SOURCES "${CMAKE_SOURCE_DIR}/source/*.c")

# Create the executable
add_executable(main ${SOURCES})