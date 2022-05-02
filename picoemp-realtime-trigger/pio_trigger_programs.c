#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "pico/stdlib.h"

#include "hardware/pio.h"
// pio-asm assembled programs:
#include "hello.pio.h"
#include "basic_trigger.pio.h"

const uint TRIGGER_PULSE_GO = PICO_DEFAULT_LED_PIN;
const uint TRIGGER_IN_PIN = 2; // 0/1 is uart
const uint TRIGGER_OUT_PIN = TRIGGER_PULSE_GO + 1; // consecutive pins so we can side-set them

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

void hello_pio_program_loop() {
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
    hello_program_init(pio, sm, offset, TRIGGER_PULSE_GO);
    
    // for hello.pio
    printf("Set LED based on LSB of uart byte\n");
    printf("?\n> ");
    while (true) {
        char chbuf;
        chbuf = getchar();
        putchar(chbuf);
        // putchar((chbuf & 1) + 0x30);
        pio_sm_put_blocking(pio, sm, chbuf);
    }
}

void basic_trigger_program_loop() {
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
    
    printf("time scale?\n");
    printf(" -    [s]\n");
    printf(" -  [m]s (default)\n");
    printf(" -  [u]s\n");
    printf(" - 8[n]s (smallest possible with 125MHz clock)\n");
    printf("> ");
    read_line();

    // 62499999 == 500ms in 8ns intervals
    #define  S_MULTIPLIER 125000000 // 1s in 8ns steps
    #define MS_MULTIPLIER 125000    // 1ms in 8ns steps, max x/y: 34359
    #define US_MULTIPLIER 125       // 1us in 8ns steps
    // 

    uint scale_multiplier = MS_MULTIPLIER;
    char scale_chars[4] = "m"; // need some more for *8n

    if (strcmp(serial_buffer, "s") == 0) {
        scale_chars[0] = '\0';
        scale_multiplier = S_MULTIPLIER;
    }
    if (strcmp(serial_buffer, "u") == 0) {
        strcpy(scale_chars, "u");
        scale_multiplier = US_MULTIPLIER;
    }
    if (strcmp(serial_buffer, "n") == 0) {
        strcpy(scale_chars, "*8n");
        scale_multiplier = 1;
    }

    while (true) {
        uint delay, length;
        printf("delay in %ss?\n> ", scale_chars);
        read_line();
        putchar('\n');
        delay = strtoul(serial_buffer, NULL, 10);
        printf("length in %ss?\n> ", scale_chars);
        read_line();
        putchar('\n');
        length = strtoul(serial_buffer, NULL, 10);
        printf("delay=0x%08x, length=0x%08x PIO cycles\n", 
            delay*scale_multiplier, length*scale_multiplier);

        pio_sm_put_blocking(pio, sm, delay*scale_multiplier);  
        pio_sm_put_blocking(pio, sm, length*scale_multiplier);
    }
}


int main() {
    stdio_init_all();
    gpio_init(TRIGGER_PULSE_GO);
    gpio_set_dir(TRIGGER_PULSE_GO, GPIO_OUT);

    gpio_init(TRIGGER_IN_PIN);
    gpio_set_dir(TRIGGER_IN_PIN, GPIO_IN);

    gpio_init(TRIGGER_OUT_PIN);
    gpio_set_dir(TRIGGER_OUT_PIN, GPIO_OUT);

    // without the sleep my laptop doesnt like the serial over usb
    // and you might not be able to attach in time to see the first message
    sleep_ms(2000);

    // printf("test?\n> ");
    // uint32_t test;
    // test = getchar();
    // printf("test: %x\n", test);

    while (true) {
        printf("program?\n");
        printf(" - [h]ello_io?\n");
        printf(" - [b]asic_trigger?\n");
        printf(" - tba?\n");
        printf("> ");
        read_line();

        if (strcmp(serial_buffer, "h") == 0 || strcmp(serial_buffer, "hello_pio") == 0) {
            hello_pio_program_loop();
            return 0;
        }

        if (strcmp(serial_buffer, "b") == 0 || strcmp(serial_buffer, "basic_trigger") == 0) {
            basic_trigger_program_loop();
            return 0;
        }
        printf("\n");
    }
}
