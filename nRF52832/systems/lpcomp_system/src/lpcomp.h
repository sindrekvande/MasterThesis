#include <nrfx_lpcomp.h>

typedef enum {
    IDLE,
    CHECKPOINT_AND_SLEEP,
    WAKEUP_AND_RECOVER,
} device_state_t;

extern device_state_t current_state;

void lpcomp_event_handler(nrf_lpcomp_event_t event);

void lpcomp_wakeup_init(void);

void lpcomp_idle_init(void);