// #include <stdio.h>

// #include "pico/stdlib.h"
// // #include "hardware/pio.h"
// // // Our assembled program:
// // #include "hello.pio.h"

// int main() {
//     stdio_init_all();

//     // const uint LED_PIN = PICO_DEFAULT_LED_PIN;
//     // gpio_init(LED_PIN);
//     // gpio_set_dir(LED_PIN, GPIO_OUT);
    
//     // const uint TRIGGER_PIN = 2; // 0/1 is uart
//     // gpio_init(TRIGGER_PIN);
//     // gpio_set_dir(TRIGGER_PIN, GPIO_OUT);

//     // // Choose which PIO instance to use (there are two instances)
//     // PIO pio = pio0;

//     // // Our assembled program needs to be loaded into this PIO's instruction
//     // // memory. This SDK function will find a location (offset) in the
//     // // instruction memory where there is enough space for our program. We need
//     // // to remember this location!
//     // uint offset = pio_add_program(pio, &hello_program);

//     // // Find a free state machine on our chosen PIO (erroring if there are
//     // // none). Configure it to run our program, and start it, using the
//     // // helper function we included in our .pio file.
//     // uint sm = pio_claim_unused_sm(pio, true);
//     // hello_program_init(pio, sm, offset, PICO_DEFAULT_LED_PIN);


//     sleep_ms(2000);
//     printf("hello pio\n");

//     while (true) {
//         char c = getchar();
//         putchar(c);
        
//         // // Blink
//         // pio_sm_put_blocking(pio, sm, 1);
//         // sleep_ms(500);
//         // // Blonk
//         // pio_sm_put_blocking(pio, sm, 0);
//         // sleep_ms(500);
//     }
        
//     return 0;
// }

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "pico/stdlib.h"

#include "hardware/pio.h"
// Our assembled program:
// #include "hello.pio.h"
#include "basic_trigger.pio.h"

static char serial_buffer[256];
void read_line() {
    memset(serial_buffer, 0, sizeof(serial_buffer));
    while(1) {
        int c = getchar();
        if(c == EOF) {
            return;
        }

        putchar(c);

        if(c == '\r') {
            return;
        }
        if(c == '\n') {
            continue;
        }

        // buffer full, just return.
        if(strlen(serial_buffer) >= 255) {
            return;
        }

        serial_buffer[strlen(serial_buffer)] = (char)c;
    }
}


int main() {
    stdio_init_all();

    const uint TRIGGER_PULSE_GO = PICO_DEFAULT_LED_PIN;
    gpio_init(TRIGGER_PULSE_GO);
    gpio_set_dir(TRIGGER_PULSE_GO, GPIO_OUT);
    
    const uint TRIGGER_IN_PIN = 2; // 0/1 is uart
    gpio_init(TRIGGER_IN_PIN);
    gpio_set_dir(TRIGGER_IN_PIN, GPIO_IN);
    
    const uint TRIGGER_OUT_PIN = TRIGGER_PULSE_GO + 1; // consecutive so we can side-set them
    gpio_init(TRIGGER_OUT_PIN);
    gpio_set_dir(TRIGGER_OUT_PIN, GPIO_OUT);

    sleep_ms(2000); // without the sleep my laptop doesnt like the serial over usb

    // Choose which PIO instance to use (there are two instances)
    PIO pio = pio0;

    // Our assembled program needs to be loaded into this PIO's instruction
    // memory. This SDK function will find a location (offset) in the
    // instruction memory where there is enough space for our program. We need
    // to remember this location!
    uint offset = pio_add_program(pio, &basic_trigger_program);

    // Find a free state machine on our chosen PIO (erroring if there are
    // none). Configure it to run our program, and start it, using the
    // helper function we included in our .pio file.
    uint sm = pio_claim_unused_sm(pio, true);
    basic_trigger_init(pio, sm, offset, 
        TRIGGER_IN_PIN, TRIGGER_PULSE_GO, TRIGGER_OUT_PIN);
    
    // printf("test?\n> ");
    // uint32_t test;
    // test = getchar();
    // printf("test: %x\n", test);
    
    // // for hello.pio
    // while (true) {
    //     printf("?\n> ");
    //     char chbuf;
    //     chbuf = getchar();
    //     putchar(chbuf);
    //     putchar(' ');
    //     putchar((chbuf & 1) + 0x30);
    //     putchar('\n');

    //     pio_sm_put_blocking(pio, sm, chbuf);
    //     // sleep_ms(500);
    //     // // Blonk
    //     // pio_sm_put_blocking(pio, sm, 0);
    //     // sleep_ms(500);
    // }

    // for basic_trigger.pio
    // 62499999 == 500ms in 8ns intervals

    #define MS_MULTIPLIER 125000 // 1ms in 8ns steps
    // max x/y: 34359

    while (true) {
        uint delay, length;
        printf("delay in ms?\n> ");
        read_line();
        putchar('\n');
        delay = strtoul(serial_buffer, NULL, 10);
        printf("length in ms?\n> ");
        read_line();
        putchar('\n');
        length = strtoul(serial_buffer, NULL, 10);
        printf("delay=%d, length=%d\n", delay, length);

        pio_sm_put_blocking(pio, sm, delay*MS_MULTIPLIER);  
        pio_sm_put_blocking(pio, sm, length*MS_MULTIPLIER);
    }

    return 0;
}
