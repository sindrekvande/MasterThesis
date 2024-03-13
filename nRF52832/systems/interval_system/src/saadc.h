#ifndef SAADC_H
#define SAADC_H

#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <nrfx_saadc.h>
#include <nrfx_timer.h>

#define NUMBER_OF_CHANNELS 1

#define SLEEP_THRESHOLD 1000 // mV
#define WAKE_UP_THRESHOLD 1500 // mV

typedef enum {
    MEASURE,
    COMMUNICATE,
    SAVE,
    RECOVER,
    NORMAL_SLEEP,
    THRESHOLD_SLEEP,
} device_state_t;

extern device_state_t current_state;

void handle_error(nrfx_err_t error_code);

void saadc_init(void);

void saadc_measure(void);

#endif