#include <zephyr/kernel.h>
#include <zephyr/sys/poweroff.h>
#include "checkpoint.h"
#include "lpcomp.h"
#include "saadc.h"
#include "bt.h"

struct k_timer my_timer;

device_state_t current_state = RECOVER;

int main(void) {
    int err;

    err = bluetooth_init(&bluetooth_callbacks, &remote_service_callbacks);
    if (err) {
        printf("Couldn't initialize Bluetooth. err: %d\n", err);
    }

    k_timer_init(&my_timer, NULL, NULL);
    saadc_init();
    nrfx_lpcomp_uninit();

    while(1) {
        switch (current_state) {
            case MEASURE:
                saadc_measure();
                checkpoint_create();
                break;
            
            case COMMUNICATE:
                advertisment_init();
                NRFX_DELAY_US(20000000);
                advertisment_uninit();
                checkpoint_create();
                break;

            case SAVE:
                break;
            
            case RECOVER:
                printf("RECOVER CHECKPOINT\n");
                //checkpoint_recover();
                current_state = MEASURE;
                break;

            case NORMAL_SLEEP:                
                printf("GOING TO SLEEP (10 minutes)\n");
                k_timer_start(&my_timer, K_MSEC(20000), K_FOREVER);
                __WFI();
                current_state = MEASURE;
                break;

            case THRESHOLD_SLEEP:
            
                break;
        }
    }
    return 0;
}
