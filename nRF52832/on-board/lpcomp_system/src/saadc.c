#include "saadc.h"

uint16_t communicate_samples[NUM_SAMPLES*SAMPLE_SIZE];
uint16_t checkpoint_pd = 0;
uint16_t recover_pd = 0;
uint16_t measure_pd = 0;
uint16_t communicate_pd = 0;
bool notif_flag = 0;

nrf_saadc_value_t raw_samples[NUMBER_OF_CHANNELS];
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
    printk("START MEASURING\n");
    nrfx_err_t err_code;

    saadc_init();
    
    for (uint16_t i = 0; i < SAMPLE_SIZE; i++) {
        err_code = nrfx_saadc_buffer_set(raw_samples, NUMBER_OF_CHANNELS);
        handle_error(err_code);

        err_code = nrfx_saadc_mode_trigger();
        handle_error(err_code);

        communicate_samples[(current_sample*SAMPLE_SIZE)+i] = raw_samples[0];

        //printf("Raw value: %d\n", communicate_samples[(current_sample*SAMPLE_SIZE)+i]);     
    }
    printf("Current sample: %d\n", current_sample);
    current_sample += 1;
    measure_pd += 1;

    // Uninint //
    nrfx_saadc_uninit();
    NRF_SAADC->INTENCLR = (SAADC_INTENCLR_END_Clear << SAADC_INTENCLR_END_Pos);
    NVIC_ClearPendingIRQ(SAADC_IRQn);
    // ---------------- //

    // SAADC reset - Workaround //
    volatile uint32_t temp1;
    volatile uint32_t temp2;
    volatile uint32_t temp3;

    temp1 = *(volatile uint32_t *)0x40007640ul;
    temp2 = *(volatile uint32_t *)0x40007644ul;
    temp3 = *(volatile uint32_t *)0x40007648ul;

    *(volatile uint32_t *)0x40007FFCul = 0ul;
    *(volatile uint32_t *)0x40007FFCul;
    *(volatile uint32_t *)0x40007FFCul = 1ul;

    *(volatile uint32_t *)0x40007640ul = temp1;
    *(volatile uint32_t *)0x40007644ul = temp2;
    *(volatile uint32_t *)0x40007648ul = temp3;
    // ---------------- //
}