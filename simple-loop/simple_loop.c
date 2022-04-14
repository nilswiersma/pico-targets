#include <stdio.h>
#include "pico/stdlib.h"

const char ping[4] = {'/', '-', '\\', '|'};

int main() {
    stdio_init_all();

    const uint LED_PIN = PICO_DEFAULT_LED_PIN;
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    
    const uint TRIGGER_PIN = 2; // 0/1 is uart
    gpio_init(TRIGGER_PIN);
    gpio_set_dir(TRIGGER_PIN, GPIO_OUT);
        
    volatile unsigned int x  = 0xA5A5A5A5;
    volatile unsigned int nx = ~x;
    volatile unsigned int z = 0;
    volatile unsigned int y = 0;

    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);

    printf("Booted\n");
    
    gpio_put(LED_PIN, 1);
    gpio_put(TRIGGER_PIN, 1);
    
    while (nx == ~x) { 
        ++y; 
        uart_get_hw(uart0)->dr = ping[y%4];
        uart_get_hw(uart0)->dr = '\r';
    }
    gpio_put(LED_PIN, 0);
    gpio_put(TRIGGER_PIN, 0);

    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);

    printf("FREE BEER! y=%08x z=%08x x=%08x nx=%08x\n", y, z, x, nx);

    while (true) {
        gpio_put(LED_PIN, 1);
        sleep_ms(100);
        gpio_put(LED_PIN, 0);
        sleep_ms(100);
    }

    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);
    gpio_put(LED_PIN, 0);


    return 0;
}
