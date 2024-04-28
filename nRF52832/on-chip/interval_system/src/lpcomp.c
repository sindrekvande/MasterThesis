#include "lpcomp.h"
#include "saadc.h"

int start_flag = 0;

void lpcomp_event_handler(nrf_lpcomp_event_t event_type) {
    if (NRF_LPCOMP->EVENTS_UP == 1) {
        NRF_LPCOMP->EVENTS_UP = 0;
        start_flag = 1;
    }
    // Clear unused interrupt events in case 
    NRF_LPCOMP->EVENTS_CROSS = 0;
    NRF_LPCOMP->EVENTS_DOWN = 0;
    NRF_LPCOMP->EVENTS_READY = 0;
}

void lpcomp_start_init(void) {   
    printk("#### LPCOMP WAKE UP INIT ####\n");
    
    nrfx_err_t err_code;

    IRQ_DIRECT_CONNECT(COMP_LPCOMP_IRQn, 4, lpcomp_event_handler, 0);

    nrfx_lpcomp_config_t config = NRFX_LPCOMP_DEFAULT_CONFIG(NRF_LPCOMP_INPUT_2); // Threshold 1.5V - AIN2 should be UART_RXD
    config.config.detection = NRF_LPCOMP_DETECT_UP;

    err_code = nrfx_lpcomp_init(&config, NULL);
    if (err_code != NRFX_SUCCESS){
        printf("Error (0x%X)\n", err_code); 
    }

    nrfx_lpcomp_enable();
}