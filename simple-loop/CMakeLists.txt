cmake_minimum_required(VERSION 3.13)
include(pico_sdk_import.cmake)
project(simple_loop_project C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
pico_sdk_init()

# version that uses USB serial
add_executable(simple_loop_usb
    simple_loop.c
)
pico_enable_stdio_usb(simple_loop_usb 1)
pico_add_extra_outputs(simple_loop_usb)
target_link_libraries(simple_loop_usb pico_stdlib)

# version that uses uart0 pins
add_executable(simple_loop_serial
    simple_loop.c
)
pico_enable_stdio_uart(simple_loop_serial 1)
pico_add_extra_outputs(simple_loop_serial)
target_link_libraries(simple_loop_serial pico_stdlib)
