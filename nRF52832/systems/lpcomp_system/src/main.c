#include <zephyr/kernel.h>
#include <zephyr/sys/poweroff.h>
#include "lpcomp.h"
#include "checkpoint.h"
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
    lpcomp_idle_init();

    while(1) {
        switch (current_state) {
            case MEASURE:
                saadc_measure();
                current_state = COMMUNICATE;
                break;
            
            case COMMUNICATE:
                advertisment_init();
                NRFX_DELAY_US(20000000);
                advertisment_uninit();
                current_state = NORMAL_SLEEP;
                break;
            
            case SAVE:
                printf("SAVE CHECKPOINT\n");
                //checkpoint_create();
                current_state = THRESHOLD_SLEEP;
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
                printf("GOING TO DEEP SLEEP\n");
                sys_poweroff();
                break;
        }
    }
    return 0;
}
