cmake_minimum_required(VERSION 3.13)
include(pico_sdk_import.cmake)
project(test_trigger_pio_project C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
pico_sdk_init()

add_executable(test_trigger_pio
    test_trigger_pio.c
)

pico_generate_pio_header(test_trigger_pio ${CMAKE_CURRENT_LIST_DIR}/hello.pio)

pico_enable_stdio_usb(test_trigger_pio 1)
pico_enable_stdio_uart(test_trigger_pio 0)
pico_add_extra_outputs(test_trigger_pio)
target_link_libraries(test_trigger_pio pico_stdlib hardware_pio)

