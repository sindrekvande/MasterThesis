#include "bt.h"
#include "nrfx_gpiote.h"

#define GPIO_PIN 15

int main(void) {
    nrfx_err_t err_code = nrfx_gpiote_init(3);
    if (err_code != NRFX_SUCCESS){
        printf("Error (0x%X)\n", err_code); 
    }

    nrfx_gpiote_output_config_t out_config = NRFX_GPIOTE_DEFAULT_OUTPUT_CONFIG;
    
    err_code = nrfx_gpiote_output_configure(GPIO_PIN, &out_config, NULL);
    if (err_code != NRFX_SUCCESS){
        printf("Error (0x%X)\n", err_code); 
    }

    int err;

    printf("Starting BT service test...\n");

    fill_saadc_values();

    err = bluetooth_init(&bluetooth_callbacks, &remote_service_callbacks);
    if (err) {
        printf("Couldn't initialize Bluetooth. err: %d", err);
    }

    advertisment_init();

    k_sleep(K_SECONDS(3));
    //k_sleep(K_MSEC(150));

    nrfx_gpiote_out_set(GPIO_PIN);
    saadc_handler();
    nrfx_gpiote_out_clear(GPIO_PIN);

    advertisment_uninit();
    
    printf("BT service test completed.\n");
}