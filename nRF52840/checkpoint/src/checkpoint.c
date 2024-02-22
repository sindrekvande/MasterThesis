#include "checkpoint.h"


int checkpoint_create() {
    const struct device *flash_dev = PARTITION_DEVICE;
    uint32_t checkpoint_data[CHECKPOINT_WORDS] = {0};
    get_program_state(checkpoint_data);

    for (uint32_t i = 0; i < CHECKPOINT_WORDS; i++) {
		uint32_t offset = PARTITION_OFFSET + (i * sizeof(uint32_t));
		printk("Writing %X at 0x%X\n", checkpoint_data[i], offset);
		if (flash_write(flash_dev, offset, &checkpoint_data[i], sizeof(checkpoint_data[i])) != 0) {
			printk("Flash write failed!\n");
			return -1;
		}
        printk("Wrote %X at address 0x%X\n", checkpoint_data[i], offset);
    }
    return 0;
}

int checkpoint_recover() {
    const struct device *flash_dev = PARTITION_DEVICE;
    uint32_t checkpoint_data[CHECKPOINT_WORDS];

    for (uint32_t i = 0; i < CHECKPOINT_WORDS; i++) {
		uint32_t offset = PARTITION_OFFSET + (i * sizeof(uint32_t));
        printk("Reading 0x%X\n", offset);
		if (flash_read(flash_dev, offset, &checkpoint_data[i], sizeof(checkpoint_data[i])) != 0) {
			printk("Flash read failed!\n");
			return -1;
		}
		printk("Read %X, from address %X\n", checkpoint_data[i], offset);
        set_program_state(checkpoint_data);
    }
    return 0;
}

void get_program_state(uint32_t * buf) { // Number of stored values needs to match CHECKPOINT_WORDS
    // Register data
    //for (int i = 0; i <= 12; ++i) {
    //    __asm__ volatile("MOV %0, R%d\n": "=r" (buf[i]) : "r" (i) : );
    //}
    __asm__ volatile("MOV %0, R0" : "=r" (buf[0]) : : );
    __asm__ volatile("MOV %0, R1" : "=r" (buf[1]) : : );
    __asm__ volatile("MOV %0, R2" : "=r" (buf[2]) : : );
    __asm__ volatile("MOV %0, R3" : "=r" (buf[3]) : : );
    __asm__ volatile("MOV %0, R4" : "=r" (buf[4]) : : );
    __asm__ volatile("MOV %0, R5" : "=r" (buf[5]) : : );
    __asm__ volatile("MOV %0, R6" : "=r" (buf[6]) : : );
    __asm__ volatile("MOV %0, R7" : "=r" (buf[7]) : : );
    __asm__ volatile("MOV %0, R8" : "=r" (buf[8]) : : );
    __asm__ volatile("MOV %0, R9" : "=r" (buf[9]) : : );
    __asm__ volatile("MOV %0, R10" : "=r" (buf[10]) : : );
    __asm__ volatile("MOV %0, R11" : "=r" (buf[11]) : : );
    __asm__ volatile("MOV %0, R12" : "=r" (buf[12]) : : );

    __asm__ volatile("MRS %0, MSP\n": "=r" (buf[13]) : : );
    __asm__ volatile("MRS %0, PSP\n": "=r" (buf[14]) : : );
    __asm__ volatile("MOV %0, LR\n": "=r" (buf[15]) : : );
    __asm__ volatile("MOV %0, PC\n": "=r" (buf[16]) : : );

    // RAM data


    // I/O data

}

void set_program_state(uint32_t * buf) {
    // Register data
    //for (int i = 0; i <= 12; ++i) {
    //    __asm__ volatile("MOV R%d, %0\n":  "r" (i) : "=r" (buf[i]));
    //}
    __asm__ volatile("MOV R0, %0" : : "r" (buf[0]) : );
    __asm__ volatile("MOV R1, %0" : : "r" (buf[1]) : );
    __asm__ volatile("MOV R2, %0" : : "r" (buf[2]) : );
    __asm__ volatile("MOV R3, %0" : : "r" (buf[3]) : );
    __asm__ volatile("MOV R4, %0" : : "r" (buf[4]) : );
    __asm__ volatile("MOV R5, %0" : : "r" (buf[5]) : );
    __asm__ volatile("MOV R6, %0" : : "r" (buf[6]) : );
    __asm__ volatile("MOV R7, %0" : : "r" (buf[7]) : );
    __asm__ volatile("MOV R8, %0" : : "r" (buf[8]) : );
    __asm__ volatile("MOV R9, %0" : : "r" (buf[9]) : );
    __asm__ volatile("MOV R10, %0" : : "r" (buf[10]) : );
    __asm__ volatile("MOV R11, %0" : : "r" (buf[11]) : );
    __asm__ volatile("MOV R12, %0" : : "r" (buf[12]) : );

    __asm__ volatile("MSR MSP, %0\n": : "r" (buf[13]) : );
    __asm__ volatile("MSR PSP, %0\n": : "r" (buf[14]) : );
    __asm__ volatile("MOV LR, %0\n": : "r" (buf[15]) : );
    __asm__ volatile("MOV PC, %0\n": : "r" (buf[16]) : );

    // RAM data
    
    // I/O data
}

int save_ram_to_flash() {
    const struct device *flash_dev = PARTITION_DEVICE;
    uint32_t offset = RAM_STORAGE_OFFSET; // Offset in flash where RAM data should be stored

    for (uint32_t *ram_ptr = (uint32_t *)RAM_START; ram_ptr < (uint32_t *)RAM_END; ram_ptr++) {
        if (flash_write(flash_dev, offset, ram_ptr, sizeof(uint32_t)) != 0) {
            printk("Flash write failed at offset 0x%X\n", offset);
            return -1;
        }
        offset += sizeof(uint32_t);
    }
    return 0;
}

int retrieve_ram_from_flash() {
    const struct device *flash_dev = PARTITION_DEVICE;
    uint32_t offset = RAM_STORAGE_OFFSET; // Offset in flash where RAM data is stored

    // Loop through the flash storage and restore it to RAM
    for (uint32_t *ram_ptr = (uint32_t *)RAM_START; ram_ptr < (uint32_t *)RAM_END; ram_ptr++) {
        uint32_t value;
        if (flash_read(flash_dev, offset, &value, sizeof(uint32_t)) != 0) {
            printk("Flash read failed at offset 0x%X\n", offset);
            return -1; 
        }
        *ram_ptr = value; // Restore value to RAM
        offset += sizeof(uint32_t);
    }
    return 0;
}

void checkpoint_test_flash() {
    uint32_t before[CHECKPOINT_WORDS] = {0};
    get_program_state(before);
    checkpoint_create();
    checkpoint_recover();
    uint32_t after[CHECKPOINT_WORDS] = {0};
    get_program_state(after);
    if (memcmp(before, after, CHECKPOINT_WORDS * sizeof(uint32_t)) != 0) {
        printk("Written data not the same as read data!");
    }
}