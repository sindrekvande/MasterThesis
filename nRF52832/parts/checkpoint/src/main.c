#include "checkpoint.h"
#include "nrfx_gpiote.h"
#include <zephyr/kernel.h>

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
    k_sleep(K_SECONDS(1));
    nrfx_gpiote_out_set(GPIO_PIN);
    checkpoint_create();
    nrfx_gpiote_out_clear(GPIO_PIN);
    k_sleep(K_SECONDS(1));
    nrfx_gpiote_out_set(GPIO_PIN);
    checkpoint_recover();
    nrfx_gpiote_out_clear(GPIO_PIN);
}
