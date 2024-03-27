#include "saadc.h"

float measure_value;

nrf_saadc_value_t samples[NUMBER_OF_CHANNELS];
nrfx_saadc_channel_t channels[NUMBER_OF_CHANNELS] = 
{
    NRFX_SAADC_DEFAULT_CHANNEL_SE(NRF_SAADC_INPUT_AIN0, 0), 
    NRFX_SAADC_DEFAULT_CHANNEL_SE(NRF_SAADC_INPUT_AIN1, 1) 
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

    err_code = nrfx_saadc_simple_mode_set((1<<0|1<<1),
                                      NRF_SAADC_RESOLUTION_12BIT,
                                      NRF_SAADC_OVERSAMPLE_DISABLED,
                                      NULL);
    handle_error(err_code);
}

void saadc_measure() {
    nrfx_err_t err_code;
 
    err_code = nrfx_saadc_buffer_set(samples, NUMBER_OF_CHANNELS);
    handle_error(err_code);

    err_code = nrfx_saadc_mode_trigger();
    handle_error(err_code);

    measure_value = (samples[0] * 3.6f * 1000) / 4095; // Changed gain in header file!
    printf("Measured value: %.2f V\n", measure_value);
}

void saadc_storage_check() {
    nrfx_err_t err_code;
 
    err_code = nrfx_saadc_buffer_set(samples, NUMBER_OF_CHANNELS);
    handle_error(err_code);

    err_code = nrfx_saadc_mode_trigger();
    handle_error(err_code);

    float storage_current = (samples[1] * 3.6f * 1000) / 4095; // Changed gain in header file!
    printf("Stored current: %.2f mV - STATE: %d\n", storage_current, current_state);

    if (current_state == MEASURE && storage_current < SLEEP_THRESHOLD) {
        printf("Current too low, going to SAVE.\n");
        current_state = SAVE;
    } else if (current_state == COMMUNICATE && storage_current < SLEEP_THRESHOLD) {
        printf("Current too low, going to SAVE.\n");
        current_state = SAVE;
    } else if (current_state == MEASURE && storage_current >= SLEEP_THRESHOLD) {
        printf("Measure completed, going to COMMUNICATE.\n");
        current_state = COMMUNICATE;
    } else if (current_state == COMMUNICATE && storage_current >= SLEEP_THRESHOLD) {
        printf("Communicate completed, going to NORMAL_SLEEP.\n");
        current_state = NORMAL_SLEEP;
    }
}