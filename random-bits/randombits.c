#include <stdio.h>
#include <string.h>

#include "pico/stdlib.h"
#include "hardware/structs/rosc.h"
#include "hardware/structs/xosc.h"


static uint32_t get_osc_randombits(void)
{
    int i;
    uint32_t ret = 0, tmp, tmp1, tmp2;
    for (i=0; i<32; ++i) {
        tmp1 = rosc_hw->randombit;
        tmp2 = rosc_hw->randombit;
        tmp = (tmp1 ^ tmp2) & 1; // basic corrector
        ret |= (tmp << i) & (1<<i);
    }
    return ret;
}

int main() {
    stdio_init_all();

    const uint LED_PIN = PICO_DEFAULT_LED_PIN;
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    
    const uint TRIGGER_PIN = 2; // 0/1 is uart
    gpio_init(TRIGGER_PIN);
    gpio_set_dir(TRIGGER_PIN, GPIO_OUT);

    sleep_ms(2000);

    printf("rosc_hw->ctrl      %08x\n", rosc_hw->ctrl);      
    printf("rosc_hw->freqa     %08x\n", rosc_hw->freqa);      
    printf("rosc_hw->freqb     %08x\n", rosc_hw->freqb);      
    printf("rosc_hw->dormant   %08x\n", rosc_hw->dormant);      
    printf("rosc_hw->div       %08x\n", rosc_hw->div);      
    printf("rosc_hw->phase     %08x\n", rosc_hw->phase);      
    printf("rosc_hw->status    %08x\n", rosc_hw->status);      
    printf("rosc_hw->randombit %08x\n", rosc_hw->randombit);      
    printf("rosc_hw->count     %08x\n", rosc_hw->count);  
    printf("");
    printf("xosc_hw->ctrl      %08x\n", xosc_hw->ctrl);
    printf("xosc_hw->status    %08x\n", xosc_hw->status);
    printf("xosc_hw->dormant   %08x\n", xosc_hw->dormant);
    printf("xosc_hw->startup   %08x\n", xosc_hw->startup);
    printf("xosc_hw->count     %08x\n", xosc_hw->count);    

    while (true) {
        printf("get_osc_randombits %08x\r",  get_osc_randombits());      
        gpio_put(LED_PIN, 1);
        gpio_put(LED_PIN, 0);
    }

    return 0;
}
