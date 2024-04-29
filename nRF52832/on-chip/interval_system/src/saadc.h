#ifndef SAADC_H
#define SAADC_H

#include <zephyr/kernel.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <nrfx_saadc.h>
#include <nrfx_timer.h>

#define NUMBER_OF_CHANNELS 1

#define NUM_SAMPLES 10
#define SAMPLE_SIZE 10

typedef enum {
    MEASURE,
    COMMUNICATE,
    RECOVER,
    SLEEP,
} device_state_t;

extern device_state_t current_state;
extern device_state_t next_state;
extern uint16_t communicate_samples[NUM_SAMPLES*SAMPLE_SIZE];
extern uint16_t current_sample;
extern bool notif_flag;


void handle_error(nrfx_err_t error_code);

void saadc_init(void);

void saadc_measure(void);

#endif