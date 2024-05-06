#ifndef SAADC_H
#define SAADC_H

#include <zephyr/kernel.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <nrfx_saadc.h>
#include <nrfx_timer.h>

#define NUMBER_OF_CHANNELS 2

#define DEEP_SLEEP_THRESHOLD 2161 // Raw value (1.9V)
#define NUM_SAMPLES 30
#define SAMPLE_SIZE 30

typedef enum {
    MEASURE,
    COMMUNICATE,
    DEEP_SLEEP,
    RECOVER,
    SLEEP,
} device_state_t;

extern device_state_t current_state;
extern device_state_t next_state;
extern uint16_t communicate_samples[NUM_SAMPLES*SAMPLE_SIZE];
extern uint16_t current_sample;
extern uint16_t checkpoint_pd;
extern uint16_t recover_pd;
extern uint16_t measure_pd;
extern uint16_t communicate_pd;
extern bool notif_flag;

void handle_error(nrfx_err_t error_code);

void saadc_init(void);

void saadc_measure(void);

void saadc_storage_check(void);

#endif