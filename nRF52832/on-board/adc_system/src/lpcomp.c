#include "lpcomp.h"
#include "saadc.h"

int start_flag = 0;

void lpcomp_event_handler(nrf_lpcomp_event_t event_type) {
    printk("Event handler - lpcomp\n");
    if (NRF_LPCOMP->EVENTS_UP == 1) {
        NRF_LPCOMP->EVENTS_UP = 0;
        start_flag = 1;
    }
    // Clear unused interrupt events in case 
    NRF_LPCOMP->EVENTS_CROSS = 0;
    NRF_LPCOMP->EVENTS_DOWN = 0;
    NRF_LPCOMP->EVENTS_READY = 0;
}

void lpcomp_wakeup_init() {   
    printk("Wake up initialize - lpcomp\n");
    
    nrfx_err_t err_code;

    IRQ_DIRECT_CONNECT(COMP_LPCOMP_IRQn, 4, lpcomp_event_handler, 0);

    nrfx_lpcomp_config_t config = NRFX_LPCOMP_DEFAULT_CONFIG(NRF_LPCOMP_INPUT_1);
    config.config.detection = NRF_LPCOMP_DETECT_UP;
    config.config.reference = NRF_LPCOMP_REF_SUPPLY_13_16; // Threshold (13/16)*3.3 = 2.68125 (2.7V)


    err_code = nrfx_lpcomp_init(&config, NULL);
    if (err_code != NRFX_SUCCESS){
        printk("Error (0x%X)\n", err_code); 
    }

    nrfx_lpcomp_enable();
}

void lpcomp_start_init() {   
    printk("Start initialize - lpcomp\n");
    
    nrfx_err_t err_code;

    IRQ_DIRECT_CONNECT(COMP_LPCOMP_IRQn, 4, lpcomp_event_handler, 0);

    nrfx_lpcomp_config_t config = NRFX_LPCOMP_DEFAULT_CONFIG(NRF_LPCOMP_INPUT_2); // Threshold 1.5V
    config.config.detection = NRF_LPCOMP_DETECT_UP;

    err_code = nrfx_lpcomp_init(&config, NULL);
    if (err_code != NRFX_SUCCESS){
        printk("Error (0x%X)\n", err_code); 
    }

    nrfx_lpcomp_enable();
}