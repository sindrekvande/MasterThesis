#include "checkpoint.h"
#include "saadc.h"
#include "lpcomp.h"
#include "bt.h"
#include <zephyr/sys/poweroff.h>
#include <zephyr/pm/state.h>
#include <zephyr/pm/device.h>
#include <zephyr/pm/pm.h>
#include <zephyr/pm/policy.h>
#include <zephyr/device.h>
#include <nrfx_glue.h>

const struct device *dev = DEVICE_DT_GET(DT_CHOSEN(zephyr_console));

device_state_t current_state = RECOVER;
device_state_t next_state = MEASURE;
uint16_t current_sample = 0;

int main(void) {
    int err;
   
    err = bluetooth_init(&bluetooth_callbacks, &remote_service_callbacks);
    if (err) {
        printf("Couldn't initialize Bluetooth. err: %d\n", err);
    }

    nrfx_lpcomp_uninit();

    while (1) {
        switch (current_state) {
            case MEASURE:
                saadc_measure();
                if (current_sample == NUM_SAMPLES){
                    next_state = COMMUNICATE;
                } else {
                    next_state = SLEEP;
                }
                saadc_storage_check();
                break;

            case COMMUNICATE:
                advertisment_init();
                while(!notif_flag){
                    k_sleep(K_MSEC(1)); 
                }  
                communicate_handler();  
                advertisment_uninit();
                next_state = SLEEP;
                saadc_storage_check();
                break;
            
            case DEEP_SLEEP:
                checkpoint_create();
                lpcomp_wakeup_init();
                printf("DEEP SLEEP\n");
                sys_poweroff();
                break;
            
            case RECOVER:
                checkpoint_recover(); // Could have to comment out checkpoint_recover and trigger checkpoint_create to get bt working
                current_state = next_state;
                break;

            case SLEEP:
                err = pm_device_action_run(dev, PM_DEVICE_ACTION_SUSPEND);
                if (err) {
                    printk("pm_device_action_run() failed (%d)\n", err);
                }

                k_sleep(K_SECONDS(3));

                err = pm_device_action_run(dev, PM_DEVICE_ACTION_RESUME);
                if (err) {
                    printk("pm_device_action_run() failed (%d)\n", err);
                }

                next_state = MEASURE;
                current_state = next_state;
                break;
        }
    }
}
