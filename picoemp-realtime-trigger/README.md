1. Set up pico-sdk, for example `export PICO_SDK_PATH=..`
2. Build both serial and usb version:
    ```
    mkdir build
    cd build
    cmake ..
    make -j4
    ```
3. For debug version: `cmake -DCMAKE_BUILD_TYPE=Debug ..` instead
