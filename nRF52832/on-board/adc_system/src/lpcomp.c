#include "lpcomp.h"
#include "saadc.h"

void lpcomp_event_handler(nrf_lpcomp_event_t event_type) {
    if (NRF_LPCOMP->EVENTS_UP == 1) {
        NRF_LPCOMP->EVENTS_UP = 0;
    }
    // Clear unused interrupt events in case 
    NRF_LPCOMP->EVENTS_CROSS = 0;
    NRF_LPCOMP->EVENTS_DOWN = 0;
    NRF_LPCOMP->EVENTS_READY = 0;
}

void lpcomp_wakeup_init() {   
    printf("#### LPCOMP WAKEUP INIT ####\n");
    
    nrfx_err_t err_code;

    IRQ_DIRECT_CONNECT(COMP_LPCOMP_IRQn, 4, lpcomp_event_handler, 0);

    nrfx_lpcomp_config_t config = NRFX_LPCOMP_DEFAULT_CONFIG(NRF_LPCOMP_INPUT_1);
    config.config.detection = NRF_LPCOMP_DETECT_UP;
    config.config.reference = NRF_LPCOMP_REF_SUPPLY_15_16; // Threshold 2.8125V

    err_code = nrfx_lpcomp_init(&config, NULL);
    if (err_code != NRFX_SUCCESS){
        printf("Error (0x%X)\n", err_code); 
    }

    nrfx_lpcomp_enable();
}