#include "saadc.h"
#include "checkpoint.h"

uint16_t communicate_samples[NUM_SAMPLES*SAMPLE_SIZE];
uint16_t checkpoint_pd = 0;
uint16_t recover_pd = 0;
uint16_t measure_pd = 0;
uint16_t communicate_pd = 0;
bool notif_flag = 0;
bool threshold_flag = 0;

#define NRFX_SAADC_KVANDE_CHANNEL_SE(_pin_p, _index)                  \
{                                                                      \
    .channel_config =                                                  \
    {                                                                  \
        NRFX_COND_CODE_1(NRF_SAADC_HAS_CH_CONFIG_RES,                  \
                         (.resistor_p = NRF_SAADC_RESISTOR_DISABLED,   \
                          .resistor_n = NRF_SAADC_RESISTOR_DISABLED,), \
                         ())                                           \
        .gain       = NRF_SAADC_GAIN1_6,                                 \
        .reference  = NRF_SAADC_REFERENCE_INTERNAL,                    \
        .acq_time   = NRFX_SAADC_DEFAULT_ACQTIME,                      \
        NRFX_COND_CODE_1(NRF_SAADC_HAS_CONV_TIME,                      \
                         (.conv_time = NRFX_SAADC_DEFAULT_CONV_TIME,), \
                         ())                                           \
        .mode       = NRF_SAADC_MODE_SINGLE_ENDED,                     \
        .burst      = NRF_SAADC_BURST_DISABLED,                        \
    },                                                                 \
    .pin_p          = (nrf_saadc_input_t)_pin_p,                       \
    .pin_n          = NRF_SAADC_INPUT_DISABLED,                        \
    .channel_index  = _index,                                          \
}

nrf_saadc_value_t raw_samples[NUMBER_OF_CHANNELS];
nrfx_saadc_channel_t channels[NUMBER_OF_CHANNELS] = {
    NRFX_SAADC_KVANDE_CHANNEL_SE(NRF_SAADC_INPUT_AIN0, 0),
    NRFX_SAADC_KVANDE_CHANNEL_SE(NRF_SAADC_INPUT_AIN1, 1)
};
 
void handle_error(nrfx_err_t error_code) {
    if (error_code!= NRFX_SUCCESS)
    {
        printk("Error (0x%X)\n", error_code); 
    }
}

void saadc_init(void) {
    //nrfx_gpiote_out_set(15);

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
    //printk("Saadc measure\n");
    nrfx_err_t err_code;

    saadc_init();
    
    for (uint16_t i = 0; i < SAMPLE_SIZE; i++) {
        err_code = nrfx_saadc_buffer_set(raw_samples, NUMBER_OF_CHANNELS);
        handle_error(err_code);

        err_code = nrfx_saadc_mode_trigger();
        handle_error(err_code);

        communicate_samples[(current_sample*SAMPLE_SIZE)+i] = raw_samples[0];

        //printk("Raw value: %d\n", communicate_samples[(current_sample*SAMPLE_SIZE)+i]);     
    }
    //printk("Current sample: %d\n", current_sample);
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

void saadc_storage_check() {
    //printk("Storage check\n");
    nrfx_err_t err_code;

    saadc_init();
    
    err_code = nrfx_saadc_buffer_set(raw_samples, NUMBER_OF_CHANNELS);
    handle_error(err_code);

    err_code = nrfx_saadc_mode_trigger();
    handle_error(err_code);

    // Uninint //
    //nrfx_gpiote_out_clear(15);
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

    //printk("Stored current: %d - STATE: %d\n", raw_samples[1], current_state);
    
    if(raw_samples[1] < CHECKPOINT_THRESHOLD && !threshold_flag){
        threshold_flag = 1;
    } else if (raw_samples[1] > CHECKPOINT_STOP_THRESHOLD && threshold_flag) {
        threshold_flag = 0;
    }

    if (threshold_flag) {
        //printk("Current too low, checkpoint.\n");
        printk("STORAGE: %d\n", raw_samples[1]);
        if (current_sample == NUM_SAMPLES) {
            current_sample = 0;
            next_state = COMMUNICATE;
            current_state = COMMUNICATE;
            checkpoint_create();
            set_first_boot_flag();
        } else {
            next_state = SLEEP;
            current_state = SLEEP;
            checkpoint_create();
            set_first_boot_flag();
        }
    } else if (current_state == MEASURE && raw_samples[1] >= CHECKPOINT_THRESHOLD && current_sample == NUM_SAMPLES) {
        //printk("Measure completed, COMMUNICATE.\n");
        printk("STORAGE: %d\n", raw_samples[1]);
        current_sample = 0;
        next_state = COMMUNICATE;
        current_state = COMMUNICATE;
    } else if (current_state == MEASURE && raw_samples[1] >= CHECKPOINT_THRESHOLD && current_sample != NUM_SAMPLES) {
        //printk("Measure completed, SLEEP.\n");
        printk("STORAGE: %d\n", raw_samples[1]);
        next_state = SLEEP;
        current_state = SLEEP;
    }else if (current_state == COMMUNICATE && raw_samples[1] >= CHECKPOINT_THRESHOLD) {
        //printk("Communicate completed, SLEEP.\n");
        printk("STORAGE: %d\n", raw_samples[1]);
        next_state = SLEEP;
        current_state = SLEEP;
    }
}