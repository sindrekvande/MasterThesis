#include <zephyr/kernel.h>
#include <zephyr/sys/poweroff.h>
#include "lpcomp.h"
#include "checkpoint.h"
#include "saadc.h"
#include "bt.h"

const struct device *dev = DEVICE_DT_GET(DT_CHOSEN(zephyr_console));

device_state_t current_state = RECOVER;
device_state_t next_state = MEASURE;
uint16_t current_sample = 0;

void print_device_address(){
    uint8_t * device_address = (uint8_t *)NRF_FICR->DEVICEADDR;
    if (NRF_FICR->DEVICEADDRTYPE & 0x01) {
        // Public address
        printf("Public MAC Address: ");
    } else {
        // Random static address
        printf("Random Static MAC Address: ");
    }
    
    printf("%02X:%02X:%02X:%02X:%02X:%02X\n",
       device_address[5], device_address[4],
       device_address[3], device_address[2],
       device_address[1], device_address[0]);
}

int main(void) {
    int err;

    err = bluetooth_init(&bluetooth_callbacks, &remote_service_callbacks);
    if (err) {
        printf("Couldn't initialize Bluetooth. err: %d\n", err);
    }
    print_device_address();

    nrfx_lpcomp_uninit();
    lpcomp_idle_init();

    while(1) {
        switch (current_state) {
            case MEASURE:
                saadc_measure();
                if (current_sample == NUM_SAMPLES){
                    current_sample = 0;
                    next_state = COMMUNICATE;
                    current_state = next_state;
                } else {
                    next_state = SLEEP;
                    current_state = next_state;
                }
                break;
            
            case COMMUNICATE:
                advertisment_init();
                while(!notif_flag){
                    k_sleep(K_MSEC(1)); 
                }
                communicate_handler();     
                advertisment_uninit();
                next_state = SLEEP;
                current_state = next_state;
                break;

            case RECOVER:
                checkpoint_recover();
                current_state = next_state;
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
                current_state = next_state;
                break;
        }
    }
    return 0;
}
