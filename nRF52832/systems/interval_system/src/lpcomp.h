#include <nrfx_lpcomp.h>

typedef enum {
    MEASURE,
    COMMUNICATE,
    SAVE,
    RECOVER,
    NORMAL_SLEEP,
    THRESHOLD_SLEEP,
} device_state_t;

extern device_state_t current_state;

void lpcomp_event_handler(nrf_lpcomp_event_t event);

void lpcomp_wakeup_init(void);