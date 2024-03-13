#include "lpcomp.h"
#include "checkpoint.h"

void handle_error(nrfx_err_t error_code) {
    if (error_code!= NRFX_SUCCESS)
    {
        printf("Error (0x%X)\n", error_code); 
    }
}

void lpcomp_event_handler(nrf_lpcomp_event_t event_type) {
    if (NRF_LPCOMP->EVENTS_UP == 1) {
        NRF_LPCOMP->EVENTS_UP = 0;
        current_state = WAKEUP_AND_RECOVER;
    }
    // Clear unused interrupt events in case 
    NRF_LPCOMP->EVENTS_CROSS = 0;
    NRF_LPCOMP->EVENTS_DOWN = 0;
    NRF_LPCOMP->EVENTS_READY = 0;
}

void lpcomp_wakeup_init(void) {   
    printf("#### LPCOMP WAKEUP INIT ####\n");
    
    nrfx_err_t err_code;

    IRQ_DIRECT_CONNECT(COMP_LPCOMP_IRQn, 4, lpcomp_event_handler, 0);

    nrfx_lpcomp_config_t config = NRFX_LPCOMP_DEFAULT_CONFIG(NRF_LPCOMP_INPUT_3); // Threshold 1.5V
    config.config.detection = NRF_LPCOMP_DETECT_UP;

    err_code = nrfx_lpcomp_init(&config, NULL);
    handle_error(err_code);

    nrfx_lpcomp_enable();
}