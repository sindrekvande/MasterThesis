#include "saadc.h"

nrf_saadc_value_t samples[NUMBER_OF_CHANNELS];
nrfx_saadc_channel_t channels[NUMBER_OF_CHANNELS] = 
{
    NRFX_SAADC_DEFAULT_CHANNEL_SE(NRF_SAADC_INPUT_AIN0, 0)
};
 
void handle_error(nrfx_err_t error_code)
{
    if (error_code!= NRFX_SUCCESS)
    {
        printf("Error (0x%X)\n", error_code); 
    }
}

void saadc_init(void)
{
    nrfx_err_t err_code;

    err_code = nrfx_saadc_init(NRFX_SAADC_DEFAULT_CONFIG_IRQ_PRIORITY);
    handle_error(err_code);
 
    err_code = nrfx_saadc_channels_config(channels, NUMBER_OF_CHANNELS);
    handle_error(err_code);

    err_code = nrfx_saadc_simple_mode_set((1<<0),
                                      NRF_SAADC_RESOLUTION_12BIT,
                                      NRF_SAADC_OVERSAMPLE_DISABLED,
                                      NULL);
    handle_error(err_code);
}

void saadc_measure() {
    nrfx_err_t err_code;
    int32_t int_part; 
 
    err_code = nrfx_saadc_buffer_set(samples, NUMBER_OF_CHANNELS);
    handle_error(err_code);

    err_code = nrfx_saadc_mode_trigger();
    handle_error(err_code);

    int32_t millivolts = (samples[0] * 1000 * 100 * 3.6) / 4095; // Changed gain in header file!
    int_part = millivolts / 100; 
    int32_t frac_part = millivolts % 100;
    printf("Measured value: %d.%02d mV\n", int_part, frac_part);
}