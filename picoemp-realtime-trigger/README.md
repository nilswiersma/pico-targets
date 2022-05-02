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

# basic_trigger
- `mov` first tx value (delay) into scratch `x`
- `mov` second tx value (pulse length) into scratch `y`
- `wait` for `gpio_trigger_in` to go high, `side-set` gpio_trigger_out_debug high
    - for debugging `nop` instead of `wait`
- count down x (`jmp` `x--`) (delay)
- count down y (`jmp` `y--`) (length), `side-set` gpio_pulse_go high, `side-set` gpio_trigger_out_debug_low
- `nop`, `side-set` gpio_pulse_go low
- `.wrap` back to two tx waits

```
; bit 0 : gpio_pulse_go
; bit 1 : gpio_trigger_out_debug
; x = delay counter
; y = pulse counter

.wrap_target
    mov x osr   side 0b00
    mov y osr   side 0b00
    wait TODO   side 0b10
delay_loop:
    jump x-- delay_loop side 0b10 
pulse_loop:
    jump y-- pulse_loop side 0b01
    nop                 side 0b00
.wrap
```

# uart_trigger
if baud-matching clock is used, then delay and length are also limited to steps in that freq (but the pio program will be simpler)

maybe use one pio for the sniffing, second pio for the glitching?

- `mov` 4 pattern bytes into scratch `x`
- `in` 8 bits into `isr` (they are now in the MSBs), check
- `in` 8 bits into `isr` (they are now in the MSBs), check
- `in` 8 bits into `isr` (they are now in the MSBs), check
`sniffing_loop`: 
- `in` 8 bits into `isr` (they are now in the MSBs), check, the `isr` is now full
- `jmp` to `trigger_up` if we saw the pattern `cmp`?
- `out` 8 bits from the `isr`, this drops the bit count back down to 24 (`out isr count`)
- `jmp` to `sniffing_loop` for a new byte
`trigger_up`
- `set` trigger pin high (or put delay / length program here)