#include "checkpoint.h"
#include "saadc.h"
#include "lpcomp.h"
#include <zephyr/sys/poweroff.h>

device_state_t current_state = WAKEUP_AND_RECOVER;

int main(void) {
    timer_init();
    saadc_init();
    nrfx_lpcomp_uninit(); 
 
    while (1) {
        switch (current_state) {
            case NORMAL_OPERATION:
                // Check current level
                __WFE();
                break;
            
            case CHECKPOINT_AND_SLEEP:
                // Create checkpoint and go to sleep
                checkpoint_create();
                lpcomp_init();
                current_state = SLEEP_CURRENT_CHECK;
                break;
            
            case WAKEUP_AND_RECOVER:
                // Wake up from sleep and recover checkpoint state
                checkpoint_recover();
                current_state = NORMAL_OPERATION;
                break;

            case SLEEP_CURRENT_CHECK:
                // Check current level in sleep
                printf("POWERING OFF\n");
                sys_poweroff();
                break;
        }
    }
}
