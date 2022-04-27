1. Set up pico-sdk, for example `export PICO_SDK_PATH=..`
2. Build both serial and usb version:
    ```
    mkdir build
    cd build
    cmake ..
    make -j4
    ```
3. For debug version: `cmake -DCMAKE_BUILD_TYPE=Debug ..` instead

125MHz sys clock == 8ns precision

2 pios with 4 statemachines each

32 ins cache

If an instruction stalls, the side-set still takes effect immediately. 
sideset occurs immediately if an instruction stalls (like `wait`)

need two side-set bits, one for pulse out, one for debug observe

- `mov` first tx value (delay) into scratch `x`
- `mov` second tx value (pulse length) into scratch `y`
- `wait` for `gpio_trigger_in` to go high, `side-set` gpio_trigger_out_debug high
    - for debugging `nop` instead of `wait`
- count down x (`jmp` `x--`) (delay)
- count down y (`jmp` `y--`) (length), `side-set` gpio_pulse_go high, `side-set` gpio_trigger_out_debug_low
- `nop`, `side-set` gpio_pulse_go low
- `.wrap` back to two tx waits

```
.wrap_target
    mov TODO x
    mov TODO y
    wait TODO side TODO
delay_loop:
    jump x-- delay_loop
pulse_loop:
    jump y-- side TODO
    nop side TODO
.wrap
```