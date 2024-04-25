#ifndef LPCOMP_H
#define LPCOMP_H

#include <nrfx_lpcomp.h>
#include <zephyr/pm/state.h>
#include <zephyr/pm/device.h>
#include <zephyr/pm/pm.h>
#include <zephyr/pm/policy.h>
#include <zephyr/device.h>

extern const struct device *dev;
extern bool lpcomp_event;

void lpcomp_event_handler(nrf_lpcomp_event_t event);

void lpcomp_wakeup_init(void);

void lpcomp_idle_init(void);

#endif