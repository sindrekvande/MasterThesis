#include "lpcomp.h"

void lpcomp_event_handler(nrf_lpcomp_event_t event_type) {
    if (NRF_LPCOMP->EVENTS_DOWN == 1) {
        printf("EVENT\n");      
        nrfx_lpcomp_uninit();
        lpcomp_wakeup_init();
        printf("SLEEP\n");
        sys_poweroff();
        NRF_LPCOMP->EVENTS_DOWN = 0;
        //current_state = RECOVER;
    }
    // Clear unused interrupt events in case 
    NRF_LPCOMP->EVENTS_CROSS = 0;
    NRF_LPCOMP->EVENTS_UP = 0;
    NRF_LPCOMP->EVENTS_READY = 0;

}

void lpcomp_idle_init(void) {   
    printf("#### LPCOMP IDLE INIT ####\n");

    nrfx_power_config_t power_config = {
        .dcdcen = 1,
    };
    nrfx_power_init(&power_config);
    
    nrfx_err_t err_code;

    IRQ_DIRECT_CONNECT(COMP_LPCOMP_IRQn, 4, lpcomp_event_handler, 0);

    nrfx_lpcomp_config_t config = NRFX_LPCOMP_DEFAULT_CONFIG(NRF_LPCOMP_INPUT_1);
    config.config.detection = NRF_LPCOMP_DETECT_DOWN;
    config.config.reference = NRF_LPCOMP_REF_SUPPLY_2_8; // Threshold 0.75V

    err_code = nrfx_lpcomp_init(&config, NULL);
    if (err_code != NRFX_SUCCESS) {
        printf("Error (0x%X)\n", err_code); 
    }

    nrfx_lpcomp_enable();
}

void lpcomp_wakeup_init(void) {   
    printf("#### LPCOMP WAKEUP INIT ####\n");
    
    nrfx_err_t err_code;

    //IRQ_DIRECT_CONNECT(COMP_LPCOMP_IRQn, 4, lpcomp_event_handler, 0);

    nrfx_lpcomp_config_t config = NRFX_LPCOMP_DEFAULT_CONFIG(NRF_LPCOMP_INPUT_1);
    config.config.detection = NRF_LPCOMP_DETECT_UP;

    err_code = nrfx_lpcomp_init(&config, NULL);
    if (err_code != NRFX_SUCCESS){
        printf("Error (0x%X)\n", err_code); 
    }

    nrfx_lpcomp_enable();
}