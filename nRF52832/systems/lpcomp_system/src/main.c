#include <zephyr/kernel.h>
#include "lpcomp.h"
#include "checkpoint.h"
#include <zephyr/sys/poweroff.h>

device_state_t current_state = WAKEUP_AND_RECOVER;

int main(void)
{
    lpcomp_idle_init();

    while(1) {
        switch (current_state) {
            case IDLE:
                // Check current level
                __WFE();
                break;
            
            case CHECKPOINT_AND_SLEEP:
                // Create checkpoint and go to sleep
                checkpoint_create();
                printf("POWERING OFF\n");
                sys_poweroff();
                break;
            
            case WAKEUP_AND_RECOVER:
                // Wake up from sleep and recover checkpoint state
                checkpoint_recover();
                current_state = IDLE;
                break;
        }
    }

    return 0;
}
