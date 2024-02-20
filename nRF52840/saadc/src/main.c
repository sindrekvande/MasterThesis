#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <nrfx_saadc.h>
#include <nrfx_timer.h>

#define NUMBER_OF_CHANNELS 4
#define TIMER_INSTANCE_ID 0
#define PERIOD_MS 5000

nrf_saadc_value_t samples[NUMBER_OF_CHANNELS];
nrfx_saadc_channel_t channels[NUMBER_OF_CHANNELS] = 
{
    NRFX_SAADC_DEFAULT_CHANNEL_SE(NRF_SAADC_INPUT_AIN0, 0), 
    NRFX_SAADC_DEFAULT_CHANNEL_SE(NRF_SAADC_INPUT_AIN1, 1), 
    NRFX_SAADC_DEFAULT_CHANNEL_SE(NRF_SAADC_INPUT_AIN2, 2), 
    NRFX_SAADC_DEFAULT_CHANNEL_SE(NRF_SAADC_INPUT_AIN3, 3)
};
 
static void handle_error(nrfx_err_t error_code)
{
    if (error_code!= NRFX_SUCCESS)
    {
        printf("Error (0x%X)\n", error_code); 
    }
}

static void timer_handler(nrf_timer_event_t event_type, void * p_context)
{
    if(event_type == NRF_TIMER_EVENT_COMPARE0)
    {
        nrfx_err_t err_code;
 
        err_code = nrfx_saadc_buffer_set(samples, NUMBER_OF_CHANNELS);
        handle_error(err_code);

        err_code = nrfx_saadc_mode_trigger();
        handle_error(err_code);

        // 3.3V reference voltage and 12-bit ADC resolution. Check if this is correct
        for (int i = 0; i < NUMBER_OF_CHANNELS; i++) {
                int32_t millivolts = (samples[i] * 3300) / 4095;
                printf("sample %d: %d mV\n", i, millivolts);
        }
    }
}

void timer_init(void) 
{
    nrfx_err_t err_code;

    nrfx_timer_t timer = NRFX_TIMER_INSTANCE(TIMER_INSTANCE_ID);
    uint32_t base_frequency = NRF_TIMER_BASE_FREQUENCY_GET(timer.p_reg);
    nrfx_timer_config_t config = NRFX_TIMER_DEFAULT_CONFIG(base_frequency);
    config.bit_width = NRF_TIMER_BIT_WIDTH_32;

    err_code = nrfx_timer_init(&timer, &config, timer_handler);
    handle_error(err_code);

#if defined(__ZEPHYR__)
    IRQ_DIRECT_CONNECT(NRFX_IRQ_NUMBER_GET(NRF_TIMER_INST_GET(TIMER_INSTANCE_ID)), IRQ_PRIO_LOWEST,
                       NRFX_TIMER_INST_HANDLER_GET(TIMER_INSTANCE_ID), 0);
#endif

    nrfx_timer_clear(&timer);
    uint32_t desired_ticks = nrfx_timer_ms_to_ticks(&timer, PERIOD_MS);
    nrfx_timer_extended_compare(&timer, NRF_TIMER_CC_CHANNEL0, desired_ticks,
                                NRF_TIMER_SHORT_COMPARE0_CLEAR_MASK, true);
    nrfx_timer_enable(&timer);
}

void saadc_init(void)
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
}

int main(void)
{
    timer_init();

    saadc_init();
 
    while (1)
    {
        __WFE();
    }
}