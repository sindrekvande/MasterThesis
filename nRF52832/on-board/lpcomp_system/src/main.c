#include <zephyr/kernel.h>
#include <zephyr/sys/poweroff.h>
#include "lpcomp.h"
#include "checkpoint.h"
#include "saadc.h"
#include "bt.h"

//#define GPIO_PIN 15

const struct device *dev = DEVICE_DT_GET(DT_CHOSEN(zephyr_console));

device_state_t current_state = RECOVER;
device_state_t next_state = MEASURE;
uint16_t current_sample = 0;

// ----- MAC ADDRESS PRINT ----- //
//void print_device_address(){
//    uint8_t * device_address = (uint8_t *)NRF_FICR->DEVICEADDR;
//    if (NRF_FICR->DEVICEADDRTYPE & 0x01) {
//        // Public address
//        printf("Public MAC Address: ");
//    } else {
//        // Random static address
//        printf("Random Static MAC Address: ");
//    }
//
//    printf("%02X:%02X:%02X:%02X:%02X:%02X\n",
//       device_address[5], device_address[4],
//       device_address[3], device_address[2],
//       device_address[1], device_address[0]);
//}

int main(void) {
//---------------------- GPIO -----------------------//
//    nrfx_err_t err_code = nrfx_gpiote_init(3);
//    if (err_code != NRFX_SUCCESS){
//        printf("Error (0x%X)\n", err_code); 
//    }
//
//    nrfx_gpiote_output_config_t out_config = NRFX_GPIOTE_DEFAULT_OUTPUT_CONFIG;
//    
//    err_code = nrfx_gpiote_output_configure(GPIO_PIN, &out_config, NULL);
//    if (err_code != NRFX_SUCCESS){
//        printf("Error (0x%X)\n", err_code); 
//    }
//---------------------------------------------------//

    int err;

    err = bluetooth_init(&bluetooth_callbacks, &remote_service_callbacks);
    if (err) {
        printf("Couldn't initialize Bluetooth. err: %d\n", err);
    }

    nrfx_lpcomp_uninit();

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
                int time = 0;
                advertisment_init();
                while(!notif_flag && time < 10){
                    k_sleep(K_SECONDS(1));
                    time++;
                }
                communicate_handler();
                advertisment_uninit();
                next_state = SLEEP;
                current_state = next_state;
                break;

            case RECOVER:
                if (!check_first_boot()) {
                    checkpoint_recover();
                } else {
                    lpcomp_start_init();
                    while(!start_flag){
                        k_sleep(K_MSEC(1));
                    }
                    nrfx_lpcomp_uninit();
                }
                lpcomp_idle_init();
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
