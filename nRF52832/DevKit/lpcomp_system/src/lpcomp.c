#include "lpcomp.h"
#include "saadc.h"
#include "checkpoint.h"
#include <zephyr/sys/poweroff.h>

void lpcomp_event_handler(nrf_lpcomp_event_t event_type) {
    pm_device_action_run(dev, PM_DEVICE_ACTION_RESUME);
    if (NRF_LPCOMP->EVENTS_DOWN == 1) {
        printk("DEEP SLEEP\n");
        nrfx_lpcomp_uninit();
        lpcomp_wakeup_init();
        checkpoint_create();
        sys_poweroff();
        NRF_LPCOMP->EVENTS_DOWN = 0;
    }
    // Clear unused interrupt events in case
    NRF_LPCOMP->EVENTS_CROSS = 0;
    NRF_LPCOMP->EVENTS_UP = 0;
    NRF_LPCOMP->EVENTS_READY = 0;
}

void lpcomp_wakeup_init(void) {   
    printf("#### LPCOMP WAKEUP INIT ####\n");
    
    nrfx_err_t err_code;

    IRQ_DIRECT_CONNECT(COMP_LPCOMP_IRQn, 4, lpcomp_event_handler, 0);

    nrfx_lpcomp_config_t config = NRFX_LPCOMP_DEFAULT_CONFIG(NRF_LPCOMP_INPUT_1); 
    config.config.detection = NRF_LPCOMP_DETECT_UP;
    config.config.reference = NRF_LPCOMP_REF_SUPPLY_15_16; // Threshold 2.8125V

    err_code = nrfx_lpcomp_init(&config, NULL);
    handle_error(err_code);

    nrfx_lpcomp_enable();
}

void lpcomp_idle_init(void) {   
    printf("#### LPCOMP IDLE INIT ####\n");
    
    nrfx_err_t err_code;

    IRQ_DIRECT_CONNECT(COMP_LPCOMP_IRQn, 4, lpcomp_event_handler, 0);

    nrfx_lpcomp_config_t config = NRFX_LPCOMP_DEFAULT_CONFIG(NRF_LPCOMP_INPUT_1);
    config.config.detection = NRF_LPCOMP_DETECT_DOWN;
    config.config.reference = NRF_LPCOMP_REF_SUPPLY_11_16; // Threshold 2.0625V

    err_code = nrfx_lpcomp_init(&config, NULL);
    handle_error(err_code);

    nrfx_lpcomp_enable();
}