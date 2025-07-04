# Compiler and flags
CC = gcc
CFLAGS = -Wall -Wextra -O2 -Iincludes

# Folders
SRC_DIR = source
INC_DIR = includes
OUT_DIR = output

# Target executable
TARGET = $(OUT_DIR)/main

# Find all .c files in source/ and corresponding .o files in output/
SRCS = $(wildcard $(SRC_DIR)/*.c)
OBJS = $(patsubst $(SRC_DIR)/%.c,$(OUT_DIR)/%.o,$(SRCS))

# Default target
all: $(TARGET)

# Link object files into the final executable
$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $(OBJS)

# Compile each .c into a .o in output/
$(OUT_DIR)/%.o: $(SRC_DIR)/%.c | $(OUT_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

# Make sure output/ exists
$(OUT_DIR):
	mkdir -p $(OUT_DIR)

# Run the program
run: $(TARGET)
	./$(TARGET)

# Clean up compiled files
clean:
	rm -rf $(OUT_DIR)

.PHONY: all clean run