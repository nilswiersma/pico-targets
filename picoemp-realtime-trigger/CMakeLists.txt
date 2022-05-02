cmake_minimum_required(VERSION 3.13)
include(pico_sdk_import.cmake)
project(pio_trigger_programs_project C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
pico_sdk_init()

add_executable(pio_trigger_programs
    pio_trigger_programs.c
)

pico_generate_pio_header(pio_trigger_programs ${CMAKE_CURRENT_LIST_DIR}/hello.pio)
pico_generate_pio_header(pio_trigger_programs ${CMAKE_CURRENT_LIST_DIR}/basic_trigger.pio)

pico_enable_stdio_usb(pio_trigger_programs 1)
pico_enable_stdio_uart(pio_trigger_programs 0)
pico_add_extra_outputs(pio_trigger_programs)
target_link_libraries(pio_trigger_programs pico_stdlib hardware_pio)

