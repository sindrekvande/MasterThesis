#ifndef SAADC_H
#define SAADC_H

#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <nrfx_saadc.h>
#include <nrfx_timer.h>

#define NUMBER_OF_CHANNELS 4
#define TIMER_INSTANCE_ID 0
#define PERIOD_MS 20000

#define SLEEP_THRESHOLD 1000 // mV
#define WAKE_UP_THRESHOLD 1500 // mV

typedef enum {
    NORMAL_OPERATION,
    CHECKPOINT_AND_SLEEP,
    WAKEUP_AND_RECOVER,
    SLEEP_CURRENT_CHECK,
} device_state_t;

extern device_state_t current_state;

void handle_error(nrfx_err_t error_code);

void saadc_init(void);

void timer_event_handler(nrf_timer_event_t event_type, void * p_context);

void timer_init(void);

#endif