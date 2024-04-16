#include <zephyr/kernel.h>
#include <zephyr/sys/poweroff.h>
#include "checkpoint.h"
#include "lpcomp.h"
#include "saadc.h"
#include "bt.h"
#include <zephyr/pm/state.h>
#include <zephyr/pm/device.h>
#include <zephyr/pm/pm.h>
#include <zephyr/pm/policy.h>
#include <zephyr/device.h>
#include <nrfx_glue.h>

const struct device *dev = DEVICE_DT_GET(DT_CHOSEN(zephyr_console));

device_state_t current_state = RECOVER;
device_state_t next_state = MEASURE;
uint32_t current_sample = 0;

int main(void) {
    int err;

    err = bluetooth_init(&bluetooth_callbacks, &remote_service_callbacks);
    if (err) {
        printf("Couldn't initialize Bluetooth. err: %d\n", err);
    }

    //lpcomp_wakeup_init();

    while(1) {
        switch (current_state) {
            case MEASURE:
                saadc_measure();
                if (current_sample == 10){
                    current_sample = 0;
                    next_state = COMMUNICATE;
                    current_state = COMMUNICATE;
                } else {
                    next_state = SLEEP;
                    current_state = SLEEP;
                }
                checkpoint_create();
                break;
            
            case COMMUNICATE:
                advertisment_init();
                k_sleep(K_SECONDS(5));      // Wait for bluetooth connection.
                communicate_handler();            // Send value if connnected
                advertisment_uninit();
                checkpoint_create();
                next_state = SLEEP;
                current_state = SLEEP;
                break;
            
            case RECOVER:
                checkpoint_recover();
                current_state = next_state;
                break;

            case SLEEP:
                printk("SLEEP\n");
                err = pm_device_action_run(dev, PM_DEVICE_ACTION_SUSPEND);
                if (err) {
                    printk("pm_device_action_run() failed (%d)\n", err);
                }

                k_sleep(K_SECONDS(3));

                err = pm_device_action_run(dev, PM_DEVICE_ACTION_RESUME);
                if (err) {
                    printk("pm_device_action_run() failed (%d)\n", err);
                }

                current_state = MEASURE;                
                break;
        }
    }
    return 0;
}
