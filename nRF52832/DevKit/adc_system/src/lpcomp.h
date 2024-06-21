#include <zephyr/kernel.h>
#include <nrfx_lpcomp.h>

void lpcomp_event_handler(nrf_lpcomp_event_t event);

void lpcomp_wakeup_init(void);