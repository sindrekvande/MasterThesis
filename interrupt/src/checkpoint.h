#include <zephyr/kernel.h>
#include <zephyr/drivers/flash.h>
#include <zephyr/storage/flash_map.h>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <stdio.h>

#ifdef CONFIG_TRUSTED_EXECUTION_NONSECURE
#define PARTITION	slot1_ns_partition
#else
#define PARTITION	slot1_partition
#endif

#define PARTITION_OFFSET	FIXED_PARTITION_OFFSET(PARTITION)
#define PARTITION_DEVICE	FIXED_PARTITION_DEVICE(PARTITION)

#define FLASH_PAGE_SIZE   4096

/**
 * @brief Creates checkpoint for current tasks
 * 
 * @return int 
 */
int checkpoint_create();

/**
 * @brief Recovers checkpoint data form befor sleep/reset
 * 
 * @return int 
 */
int checkpoint_recover();
