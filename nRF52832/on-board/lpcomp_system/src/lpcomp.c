#include "lpcomp.h"
#include "saadc.h"
#include "checkpoint.h"
#include <zephyr/sys/poweroff.h>

int start_flag = 0;

void lpcomp_event_handler(nrf_lpcomp_event_t event_type) {
    pm_device_action_run(dev, PM_DEVICE_ACTION_RESUME);
    if (NRF_LPCOMP->EVENTS_DOWN == 1) {
        printk("DEEP SLEEP\n");
        nrfx_lpcomp_uninit();
        lpcomp_wakeup_init();
        checkpoint_create();
        set_first_boot_flag();
        sys_poweroff();
        NRF_LPCOMP->EVENTS_DOWN = 0;
    } else if (NRF_LPCOMP->EVENTS_UP == 1){
        NRF_LPCOMP->EVENTS_UP = 0;
        start_flag = 1;
    }

    // Clear unused interrupt events in case
    NRF_LPCOMP->EVENTS_CROSS = 0;
    NRF_LPCOMP->EVENTS_READY = 0;
}

void lpcomp_wakeup_init(void) {   
    printf("#### LPCOMP WAKEUP INIT ####\n");
    
    nrfx_err_t err_code;

    IRQ_DIRECT_CONNECT(COMP_LPCOMP_IRQn, 4, lpcomp_event_handler, 0);

    nrfx_lpcomp_config_t config = NRFX_LPCOMP_DEFAULT_CONFIG(NRF_LPCOMP_INPUT_1); 
    config.config.detection = NRF_LPCOMP_DETECT_UP;
    config.config.reference = NRF_LPCOMP_REF_SUPPLY_7_8; // Threshold 2.625V (2.5V)

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
    config.config.reference = NRF_LPCOMP_REF_SUPPLY_5_8; // Threshold 1.875 (1.9V)

    err_code = nrfx_lpcomp_init(&config, NULL);
    handle_error(err_code);

    nrfx_lpcomp_enable();
}

void lpcomp_start_init(void) {   
    printk("#### LPCOMP START INIT ####\n");
    
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