#include <zephyr/kernel.h>
#include <zephyr/sys/poweroff.h>
#include "lpcomp.h"
#include "checkpoint.h"
#include "saadc.h"
#include "bt.h"

const struct device *dev = DEVICE_DT_GET(DT_CHOSEN(zephyr_console));

device_state_t current_state = RECOVER;
device_state_t next_state = MEASURE;
uint32_t current_sample = 0;
bool lpcomp_event = 0;

int main(void) {
    int err;

    err = bluetooth_init(&bluetooth_callbacks, &remote_service_callbacks);
    if (err) {
        printf("Couldn't initialize Bluetooth. err: %d\n", err);
    }

    nrfx_lpcomp_uninit();
    lpcomp_idle_init();

    while(1) {
        switch (current_state) {
            case MEASURE:
                saadc_measure();
                if (current_sample == 10){
                    current_sample = 0;
                    next_state = COMMUNICATE;
                    if (!lpcomp_event){
                        current_state = next_state;
                    }
                } else {
                    next_state = SLEEP;
                    if (!lpcomp_event){
                        current_state = next_state;
                    }
                }
                break;
            
            case COMMUNICATE:
                advertisment_init();
                k_sleep(K_SECONDS(5));      // Wait for bluetooth connection.
                communicate_handler();            // Send value if connnected
                advertisment_uninit();
                next_state = SLEEP;
                if (!lpcomp_event){
                    current_state = next_state;
                }
                break;

            case RECOVER:
                checkpoint_recover();
                if (!lpcomp_event){
                    current_state = next_state;
                }
                break;

            case SLEEP:
                printk("SLEEP\n");
                err = pm_device_action_run(dev, PM_DEVICE_ACTION_SUSPEND);
                if (err) {
                    printk("pm_device_action_run(suspend) failed (%d)\n", err);
                }

                k_sleep(K_SECONDS(3));

                err = pm_device_action_run(dev, PM_DEVICE_ACTION_RESUME);
                if (err) {
                    printk("pm_device_action_run(resume) failed (%d)\n", err);
                }

                next_state = MEASURE;
                if (!lpcomp_event){
                    current_state = next_state;
                }
                break;

            //case DEEP_SLEEP:
            //    printk("DEEP SLEEP\n");
            //    nrfx_lpcomp_uninit();
            //    lpcomp_wakeup_init();
            //    checkpoint_create();
            //    sys_poweroff();
            //break;
        }
    }
    return 0;
}
