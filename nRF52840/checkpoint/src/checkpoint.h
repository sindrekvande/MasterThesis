#include <zephyr/kernel.h>
#include <zephyr/drivers/flash.h>
#include <zephyr/storage/flash_map.h>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <stdio.h>  
#include <stdint.h>

#ifdef CONFIG_TRUSTED_EXECUTION_NONSECURE
#define PARTITION	slot1_ns_partition
#else
#define PARTITION	slot1_partition
#endif

#define PARTITION_OFFSET	FIXED_PARTITION_OFFSET(PARTITION)
#define PARTITION_DEVICE	FIXED_PARTITION_DEVICE(PARTITION)

#define FLASH_PAGE_SIZE   4096 // Correct
#define CHECKPOINT_WORDS    17 // Number of registers

#define RAM_AND_FLASH_OFFSET 0x00001000 // Correct

#define RAM_START   0x20000000 // Correct
#define RAM_END     0x20000100
//#define RAM_END     0x20038000 // Correct

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

/**
 * @brief Test if flash memory is behaving as expected.
 * 
 * @return int 
 */
void checkpoint_test_flash();

/**
 * @brief Get the program state and store to buffer
 * 
 * @param buf[out]
 * @return int 
 */
void get_program_state(uint32_t * buf);

/**
 * @brief Set the program state from values in buffer
 * 
 * @param buf[in] 
 * @return int 
 */
void set_program_state(uint32_t * buf);

int save_ram_to_flash();

int retrieve_ram_from_flash();