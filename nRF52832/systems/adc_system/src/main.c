#include "checkpoint.h"
#include "saadc.h"
#include "lpcomp.h"
#include "bt.h"
#include <zephyr/sys/poweroff.h>
#include <nrfx_glue.h>

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

    while (1) {
        switch (current_state) {
            case MEASURE:
                saadc_measure();
                saadc_storage_check();
                break;

            case COMMUNICATE:
                advertisment_init();
                NRFX_DELAY_US(20000000);    // Wait for bluetooth connection.
                saadc_handler();            // Send value if connnected
                NRFX_DELAY_US(5000000);     // Give time to finish sending
                advertisment_uninit();
                NRFX_DELAY_US(1000000);     // Give time to uninit adv
                saadc_storage_check();
                break;
            
            case SAVE:
                printf("SAVE CHECKPOINT\n");
                //checkpoint_create();
                lpcomp_init();
                current_state = THRESHOLD_SLEEP;
                break;
            
            case RECOVER:
                printf("RECOVER CHECKPOINT\n");
                //checkpoint_recover();
                current_state = MEASURE;
                break;

            case NORMAL_SLEEP:
                printf("GOING TO SLEEP (10 minutes)\n");
                k_timer_start(&my_timer, K_MSEC(5000), K_FOREVER);
                __WFI();
                current_state = MEASURE;
                break;

            case THRESHOLD_SLEEP:
                printf("GOING TO DEEP SLEEP\n");
                sys_poweroff();
                break;
        }
    }
}
