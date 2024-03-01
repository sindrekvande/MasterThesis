#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/pm/pm.h>
#include <zephyr/drivers/gpio.h>
#include <hal/nrf_power.h>
#include <nrfx_lpcomp.h>
#include <nrfx_gpiote.h>
#include "nrfx.h"
#include <zephyr/sys/poweroff.h>

void handle_error(nrfx_err_t error_code) {
    if (error_code!= NRFX_SUCCESS) {
        printk("Error (0x%X)\n", error_code); 
    }
}

void lpcomp_event_handler(nrf_lpcomp_event_t event_type) {
    printk("EVENT");  
    if (NRF_LPCOMP->EVENTS_UP == 1) {
        NRF_LPCOMP->EVENTS_UP = 0;
        printk("WAKE UP!");
    }
    NRF_LPCOMP->EVENTS_DOWN = 0;
    NRF_LPCOMP->EVENTS_CROSS = 0;
    NRF_LPCOMP->EVENTS_READY = 0;
}

void lpcomp_init(void) {   
    nrfx_err_t err_code;

    IRQ_DIRECT_CONNECT(COMP_LPCOMP_IRQn, 4, lpcomp_event_handler, 0);

    nrfx_lpcomp_config_t config = NRFX_LPCOMP_DEFAULT_CONFIG(NRF_LPCOMP_INPUT_3);
    config.config.detection = NRF_LPCOMP_DETECT_UP;

    err_code = nrfx_lpcomp_init(&config, NULL);
    handle_error(err_code);

    nrfx_lpcomp_enable();
}

int main(void) {
    lpcomp_init();
    printk("POWER OFF\n");
    while(1) {
        sys_poweroff();
    }
    return 0;
}
