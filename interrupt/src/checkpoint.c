#include "checkpoint.h"


int checkpoint_create() {
    const struct device *flash_dev = PARTITION_DEVICE;
    flash_write();
}

int checkpoint_recover() {
    const struct device *flash_dev = PARTITION_DEVICE;
    flash_read();
}