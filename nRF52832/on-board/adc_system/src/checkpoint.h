#ifndef CHECKPOINT_H
#define CHECKPOINT_H

#include <zephyr/kernel.h>
#include <zephyr/drivers/flash.h>
#include <zephyr/storage/flash_map.h>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>

#ifdef CONFIG_TRUSTED_EXECUTION_NONSECURE
#define PARTITION	slot1_ns_partition
#else
#define PARTITION	slot1_partition
#endif

#define PARTITION_OFFSET	FIXED_PARTITION_OFFSET(PARTITION)
#define PARTITION_DEVICE	FIXED_PARTITION_DEVICE(PARTITION)

#define FLASH_PAGE_SIZE     4096 
#define CHECKPOINT_WORDS    7+(NUM_SAMPLES*SAMPLE_SIZE) // Number of registers (FULL SOLUTION: 19)

#define RAM_START   0x20000000 
#define RAM_END     0x20000010

#define FIRST_BOOT_FLAG_ADDR 0x42000
#define FIRST_BOOT_FLAG_VALUE 0xA5A5A5A5

bool check_first_boot();

/**
 * @brief Creates checkpoint for current tasks.
 * 
 * @return int 
 */
int checkpoint_create();

/**
 * @brief Recovers checkpoint data form befor sleep/reset.
 * 
 * @return int 
 */
int checkpoint_recover();

/** @brief Test if flash memory is behaving as expected. **/
void checkpoint_test_flash();

/**
 * @brief Get the program state and store to buffer
 * 
 * @param buf[out]
 */
void get_program_state(uint32_t * buf);

/**
 * @brief Set the program state from values in buffer
 * 
 * @param buf[in] 
 */
void set_program_state(uint32_t * buf);

int save_ram_to_flash();

int retrieve_ram_from_flash();

#endif