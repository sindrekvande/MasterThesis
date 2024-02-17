#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <nrfx_saadc.h>

#define NUMBER_OF_CHANNELS 4

nrf_saadc_value_t samples[NUMBER_OF_CHANNELS];
nrfx_saadc_channel_t channels[NUMBER_OF_CHANNELS] = {NRFX_SAADC_DEFAULT_CHANNEL_SE(NRF_SAADC_INPUT_AIN0, 0), 
                                                     NRFX_SAADC_DEFAULT_CHANNEL_SE(NRF_SAADC_INPUT_AIN1, 1), 
                                                     NRFX_SAADC_DEFAULT_CHANNEL_SE(NRF_SAADC_INPUT_AIN2, 2), 
                                                     NRFX_SAADC_DEFAULT_CHANNEL_SE(NRF_SAADC_INPUT_AIN3, 3)};
 
static void handle_error(nrfx_err_t error_code)
{
    if (error_code!= NRFX_SUCCESS)
    {
        printf("Error (0x%X)\n", error_code); 
    }
}

int main(void)
{
    nrfx_err_t err_code;
 
    err_code = nrfx_saadc_init(NRFX_SAADC_DEFAULT_CONFIG_IRQ_PRIORITY);
    handle_error(err_code);
 
    err_code = nrfx_saadc_channels_config(channels, NUMBER_OF_CHANNELS);
    handle_error(err_code);

    err_code = nrfx_saadc_simple_mode_set((1<<0|1<<1|1<<2|1<<3),
                                          NRF_SAADC_RESOLUTION_12BIT,
                                          NRF_SAADC_OVERSAMPLE_4X,
                                          NULL);
    handle_error(err_code);
 
    err_code = nrfx_saadc_buffer_set(samples, NUMBER_OF_CHANNELS);
    handle_error(err_code);
 
    while (1)
    {
        err_code = nrfx_saadc_mode_trigger();
        handle_error(err_code);

        // 3.3V reference voltage and 12-bit ADC resolution. Check if this is correct
        for (int i = 0; i < NUMBER_OF_CHANNELS; i++) {
                int32_t millivolts = (samples[i] * 3300) / 4095;
                printf("sample %d: %d mV\n", i, millivolts);
        }
        
        NRFX_DELAY_US(5000000);   
    }
}