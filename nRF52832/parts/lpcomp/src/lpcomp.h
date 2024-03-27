#ifndef LPCOMP_H
#define LPCOMP_H

#include <zephyr/kernel.h>
#include <zephyr/sys/poweroff.h>
#include <nrfx_lpcomp.h>
#include <nrfx_power.h>

void lpcomp_event_handler(nrf_lpcomp_event_t event);

void lpcomp_idle_init(void);

void lpcomp_wakeup_init(void);

#endif