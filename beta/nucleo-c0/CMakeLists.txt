#############################################################################################################################
# file:  CMakeLists.txt
# brief: Template for STM32CubeIDE + GCC toolchain project build
#
# usage:
#  cmake -DCMAKE_TOOLCHAIN_FILE=cubeide-gcc.cmake -S ./ -B build -DCMAKE_BUILD_TYPE=Debug
#  cmake --build build -- -j
#############################################################################################################################
cmake_minimum_required(VERSION 3.20)

###################### CONSTANTS ######################################
set(PROJECT_TYPE_EXECUTABLE      "exe")
set(PROJECT_TYPE_STATIC_LIBRARY  "static-lib")
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(MCPU_CORTEX_M0       "-mcpu=cortex-m0")
set(MCPU_CORTEX_M0PLUS   "-mcpu=cortex-m0plus")
set(MCPU_CORTEX_M3       "-mcpu=cortex-m3")
set(MCPU_CORTEX_M4       "-mcpu=cortex-m4")
set(MCPU_CORTEX_M7       "-mcpu=cortex-m7")
set(MCPU_CORTEX_M33      "-mcpu=cortex-m33")
set(MCPU_CORTEX_M55      "-mcpu=cortex-m55")
set(MCPU_CORTEX_M85      "-mcpu=cortex-m85")

set(MFPU_FPV4_SP_D16    "-mfpu=fpv4-sp-d16")
set(MFPU_FPV4           "-mfpu=vfpv4")
set(MFPU_FPV5_D16       "-mfpu=fpv5-d16")

set(RUNTIME_LIBRARY_REDUCED_C        "--specs=nano.specs")
set(RUNTIME_LIBRARY_STD_C            "")
set(RUNTIME_LIBRARY_SYSCALLS_MINIMAL "--specs=nosys.specs")
set(RUNTIME_LIBRARY_SYSCALLS_NONE    "")

set(MFLOAT_ABI_SOFTWARE  "-mfloat-abi=soft")
set(MFLOAT_ABI_HARDWARE  "-mfloat-abi=hard")
set(MFLOAT_ABI_MIX       "-mfloat-abi=softfp")
#######################################################################

###################### VARIABLES ######################################
set(PROJECT_NAME             "stm32c0")
set(PROJECT_TYPE             "exe")                        # exe or static-lib
set(LINKER_SCRIPT            "${CMAKE_SOURCE_DIR}/linker/STM32C051C8TX_FLASH.ld")

set(MCPU                     "${MCPU_CORTEX_M0PLUS}")      # Target CPU
set(MFPU                    "")                             # Add FP flags if needed
set(MFLOAT_ABI              "")                             # "-mfloat-abi=soft" or other

set(RUNTIME_LIBRARY          "${RUNTIME_LIBRARY_REDUCED_C}")
set(RUNTIME_LIBRARY_SYSCALLS "${RUNTIME_LIBRARY_SYSCALLS_MINIMAL}")

set(PROJECT_SOURCES
    Core/Src/main.c
    Core/Src/system_stm32c0xx.c
    Core/Src/syscalls.c
    Core/Src/sysmem.c
    Core/Src/stm32c0xx_hal_msp.c
    Core/Src/stm32c0xx_it.c
    Core/Startup/startup_stm32c051c8tx.s
    Drivers/STM32C0xx_HAL_Driver/Src/stm32c0xx_hal.c
    Drivers/STM32C0xx_HAL_Driver/Src/stm32c0xx_hal_rcc.c
    Drivers/STM32C0xx_HAL_Driver/Src/stm32c0xx_hal_gpio.c
    Drivers/STM32C0xx_HAL_Driver/Src/stm32c0xx_hal_cortex.c
    Drivers/STM32C0xx_HAL_Driver/Src/stm32c0xx_hal_dma.c
    Drivers/STM32C0xx_HAL_Driver/Src/stm32c0xx_hal_exti.c
    Drivers/STM32C0xx_HAL_Driver/Src/stm32c0xx_hal_flash_ex.c
    Drivers/STM32C0xx_HAL_Driver/Src/stm32c0xx_hal_pwr_ex.c
    Drivers/STM32C0xx_HAL_Driver/Src/stm32c0xx_hal_pwr.c
    Drivers/STM32C0xx_HAL_Driver/Src/stm32c0xx_hal_rcc_ex.c
)

set(PROJECT_DEFINES
    # Add defines here, e.g. STM32C0xx
    USE_HAL_DRIVER
    STM32C051xx
)

set(PROJECT_INCLUDES
    Core/Inc
    Core/Startup
    Drivers/CMSIS/Include
    Drivers/CMSIS/Device/ST/STM32C0xx/Include
    Drivers/STM32C0xx_HAL_Driver/Inc
)

#######################################################################

################## PROJECT SETUP ######################################
project(${PROJECT_NAME} C ASM)

enable_language(ASM)

if (${PROJECT_TYPE} STREQUAL ${PROJECT_TYPE_EXECUTABLE})
    add_executable(${PROJECT_NAME} ${PROJECT_SOURCES})
    add_custom_command(
        TARGET ${PROJECT_NAME} POST_BUILD
        COMMAND ${CMAKE_SIZE} $<TARGET_FILE:${PROJECT_NAME}>
    )
elseif (${PROJECT_TYPE} STREQUAL ${PROJECT_TYPE_STATIC_LIBRARY})
    add_library(${PROJECT_NAME} STATIC ${PROJECT_SOURCES})
endif()

add_compile_definitions(${PROJECT_DEFINES})
include_directories(${PROJECT_INCLUDES})

set(CMAKE_EXECUTABLE_SUFFIX ".elf")
set(CMAKE_STATIC_LIBRARY_SUFFIX ".a")

# Compose C flags carefully without semicolons:
set(CMAKE_C_FLAGS "${MCPU} -std=gnu11 ${MFPU} ${MFLOAT_ABI} ${RUNTIME_LIBRARY} -mthumb -Wall -Werror")

set(CMAKE_ASM_FLAGS "${CMAKE_C_FLAGS} -x assembler-with-cpp")

set(CMAKE_EXE_LINKER_FLAGS
    "-T${LINKER_SCRIPT} \
    ${RUNTIME_LIBRARY_SYSCALLS} \
    -Wl,-Map=${PROJECT_NAME}.map \
    -Wl,--gc-sections \
    -static \
    -Wl,--start-group \
    -lc \
    -lm \
    -Wl,--end-group"
)