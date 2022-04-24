cmake_minimum_required(VERSION 3.13)
include(pico_sdk_import.cmake)
project(test_aes_project C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
pico_sdk_init()

add_subdirectory(${CMAKE_CURRENT_LIST_DIR}/../lib/tiny-AES-c lib/tiny-AES-c)
include_directories(${CMAKE_CURRENT_LIST_DIR}/../lib/)

add_executable(test_aes
    test_aes.c
)

pico_enable_stdio_usb(test_aes 1)
pico_enable_stdio_uart(test_aes 0)
pico_add_extra_outputs(test_aes)
target_link_libraries(test_aes pico_stdlib)
target_link_libraries(test_aes tiny-aes)



# target_link_libraries (${PROJECT_NAME} tiny-aes)