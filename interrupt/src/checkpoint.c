#include "checkpoint.h"


int checkpoint_create() {
    const struct device *flash_dev = PARTITION_DEVICE;
	uint32_t i, offset;

    uint32_t checkpoint_data[CHECKPOINT_WORDS] = 0;
    get_program_state(checkpoint_data);

    for (i = 0U; i < ARRAY_SIZE(checkpoint_data); i++) {
		offset = PARTITION_OFFSET + (i << 2) + 1;
		printk("Writing %X at 0x%X\n", checkpoint_data[i], offset);
		if (flash_write(flash_dev, offset, &checkpoint_data[i], sizeof(uint32_t)) != 0) {
			printk("Flash write failed!\n");
			return -1;
		}
        printk("Wrote %X at address 0x%X\n", checkpoint_data[i], offset)
    }
}

int checkpoint_recover() {
    const struct device *flash_dev = PARTITION_DEVICE;
    uint32_t read_word = 0U;
	uint32_t i, offset;

    uint32_t checkpoint_data[CHECKPOINT_WORDS];

    for (i = 0U; i < ARRAY_SIZE(checkpoint_data); i++) {
		offset = PARTITION_OFFSET + (i << 2) + 1;
        printk("Reading 0x%X\n", offset);
		if (flash_read(flash_dev, offset, &read_word, sizeof(uint32_t)) != 0) {
			printk("Flash read failed!\n");
			return -1;
		}
		printk("Read %X, from address %X\n", read_word, offset);
        checkpoint_data[i] = read_word;
    }
}

int get_program_state(uint32_t * buf) { // Number of stored values needs to match CHECKPOINT_WORDS
    // Register data
    for (int i = 0; i <= 12; ++i) {
        asm volatile("MOV %0, R%d\n": "=r" (buf[i]) : "r" (i) : );
    }
    asm volatile("MRS %0, MSP\n": "=r" (buf[13]) : : );
    asm volatile("MRS %0, PSP\n": "=r" (buf[14]) : : );
    asm volatile("MRS %0, LR\n": "=r" (buf[15]) : : );
    asm volatile("MRS %0, PC\n": "=r" (buf[16]) : : );

    // RAM data
    

    // I/O data

}

int set_program_state(uint32_t * buf) {
    // Register data
    for (int i = 0; i <= 12; ++i) {
        asm volatile("MOV R%d, %0\n":  "r" (i) :"=r" (buf[i]) : );
    }
    asm volatile("MRS MSP, %0\n": : "=r" (buf[13]) : );
    asm volatile("MRS PSP, %0\n": : "=r" (buf[14]) : );
    asm volatile("MRS LR, %0\n": : "=r" (buf[15]) : );
    asm volatile("MRS PC, %0\n": : "=r" (buf[16]) : );

    // RAM data
    

    // I/O data
}

int checkpoint_test_flash() {
    uint32_t before[CHECKPOINT_WORDS] = {0};
    get_program_state(before);
    checkpoint_create();
    checkpoint_recover();
    uint32_t after[CHECKPOINT_WORDS] = {0};
    get_program_state(after);
    if (before != after) {
        printk("Written data not the same as read data!")
    }
}