Simple loop program that needs no trigger. Serial version is more usable than the USB version, as you will be hitting the serial->usb converter, and resetting the pico via RUN pin will reset and reload the USB interface as well which is annoying.

1. Set up pico-sdk, for example `export PICO_SDK_PATH=..`
2. Build both serial and usb version:
    ```
    mkdir build
    cd build
    cmake ..
    make -j4
    ```
3. For debug version: `cmake -DCMAKE_BUILD_TYPE=Debug ..` instead
