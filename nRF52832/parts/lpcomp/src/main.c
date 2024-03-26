#include "lpcomp.h"
#include <zephyr/pm/state.h>
#include <zephyr/pm/device.h>
#include <zephyr/pm/pm.h>
#include <zephyr/pm/policy.h>
#include <zephyr/device.h>

static const struct device *dev = DEVICE_DT_GET(DT_CHOSEN(zephyr_console));

int main(void) {
    lpcomp_idle_init();

    int ret = pm_device_action_run(dev, PM_DEVICE_ACTION_SUSPEND);
		if (ret < 0) {
			printk("Failure to suspend device!\n");
		}
    
    k_sleep(K_FOREVER);
}
