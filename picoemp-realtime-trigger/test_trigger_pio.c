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
#include "hello.pio.h"

int main() {
    stdio_init_all();

    const uint LED_PIN = PICO_DEFAULT_LED_PIN;
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    
    const uint TRIGGER_PIN = 2; // 0/1 is uart
    gpio_init(TRIGGER_PIN);
    gpio_set_dir(TRIGGER_PIN, GPIO_OUT);

    sleep_ms(2000); // without the sleep my laptop doesnt like the serial over usb


    // Choose which PIO instance to use (there are two instances)
    PIO pio = pio0;

    // Our assembled program needs to be loaded into this PIO's instruction
    // memory. This SDK function will find a location (offset) in the
    // instruction memory where there is enough space for our program. We need
    // to remember this location!
    uint offset = pio_add_program(pio, &hello_program);

    // Find a free state machine on our chosen PIO (erroring if there are
    // none). Configure it to run our program, and start it, using the
    // helper function we included in our .pio file.
    uint sm = pio_claim_unused_sm(pio, true);
    hello_program_init(pio, sm, offset, PICO_DEFAULT_LED_PIN);
    
    // printf("test?\n> ");
    // uint32_t test;
    // test = getchar();
    // printf("test: %x\n", test);
    

    while (true) {
        printf("?\n> ");
        char chbuf;
        chbuf = getchar();
        putchar(chbuf);
        putchar(' ');
        putchar((chbuf & 1) + 0x30);
        putchar('\n');

        // Blink
        pio_sm_put_blocking(pio, sm, chbuf);
        // sleep_ms(500);
        // // Blonk
        // pio_sm_put_blocking(pio, sm, 0);
        // sleep_ms(500);
    }

    return 0;
}
