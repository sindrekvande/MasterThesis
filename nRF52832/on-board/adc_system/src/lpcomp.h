#include <zephyr/kernel.h>
#include <nrfx_lpcomp.h>

extern int start_flag;

void lpcomp_event_handler(nrf_lpcomp_event_t event);

void lpcomp_wakeup_init(void);

void lpcomp_start_init(void);