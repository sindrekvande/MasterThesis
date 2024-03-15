#include <zephyr/kernel.h>
#include <nrfx_lpcomp.h>

void lpcomp_event_handler(nrf_lpcomp_event_t event);

void lpcomp_init(void);

void test_lpcomp_service(void);