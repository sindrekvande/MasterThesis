#include "checkpoint.h"

const struct device *flash_dev = PARTITION_DEVICE;
uint32_t checkpoint_data[CHECKPOINT_WORDS] = {0};

int checkpoint_create() {
    printk("#### CREATING CHECKPOINT ###\n");
    get_program_state(checkpoint_data);

    uint32_t offset = PARTITION_OFFSET;
    if (flash_erase(flash_dev, offset, FLASH_PAGE_SIZE) != 0) {
        printk("Flash erase failed at offset 0x%X\n", offset);
        return -1;
    }

    for (uint32_t i = 0; i < CHECKPOINT_WORDS; i++) {
		if (flash_write(flash_dev, offset + (i * sizeof(uint32_t)), &checkpoint_data[i], sizeof(checkpoint_data[i])) != 0) {
			printk("Flash write failed at offset 0x%08X\n", offset + (i * sizeof(uint32_t)));
			return -1;
		}
        printk("Wrote 0x%08X at address 0x%08X\n", checkpoint_data[i], offset + (i * sizeof(uint32_t)));
    }
    return save_ram_to_flash();
}

int checkpoint_recover() {
    printk("#### RECOVERING CHECKPOINT ####\n");
    uint32_t offset = PARTITION_OFFSET;

    for (uint32_t i = 0; i < CHECKPOINT_WORDS; i++) {
		if (flash_read(flash_dev, offset + (i * sizeof(uint32_t)), &checkpoint_data[i], sizeof(checkpoint_data[i])) != 0) {
			printk("Flash read failed at offset 0x%08X\n", offset + (i * sizeof(uint32_t)));
			return -1;
		}
		printk("Read 0x%08X, from address 0x%08X\n", checkpoint_data[i], offset + (i * sizeof(uint32_t)));
    }
    set_program_state(checkpoint_data);
    return retrieve_ram_from_flash();
}

void get_program_state(uint32_t * buf) { // Number of stored values needs to match CHECKPOINT_WORDS
    printk("#### GET PROGRAM STATE ####\n");

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

    //print_buffer(buf, CHECKPOINT_WORDS);
}

void set_program_state(uint32_t * buf) {
    printk("#### SET PROGRAM STATE ####\n");

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

    //print_buffer(buf, CHECKPOINT_WORDS);
}

int save_ram_to_flash() {
    printk("#### SAVE RAM TO FLASH ####\n");
    uint32_t offset = PARTITION_OFFSET + CHECKPOINT_WORDS * sizeof(uint32_t); 

    for (uint32_t *ram_ptr = (uint32_t *)RAM_START; ram_ptr < (uint32_t *)RAM_END; ram_ptr++) {
        if (offset % FLASH_PAGE_SIZE == 0) {
            if (flash_erase(flash_dev, offset, FLASH_PAGE_SIZE) != 0) {
                printk("Flash erase failed at offset 0x%08X\n", offset);
                return -1;
            }
        }
        if (flash_write(flash_dev, offset, ram_ptr, sizeof(uint32_t)) != 0) { 
            printk("Flash write failed at offset 0x%08X\n", offset);
            return -1;
        }
        printk("Wrote %d from RAM %p at FLASH 0x%08X\n", *ram_ptr, ram_ptr, offset);
        offset += sizeof(uint32_t);
    }
    return 0;
}

int retrieve_ram_from_flash() {
    printk("#### RETRIVE RAM FROM FLASH ####\n");
    uint32_t offset = PARTITION_OFFSET + (CHECKPOINT_WORDS * sizeof(uint32_t)); 

    for (uint32_t *ram_ptr = (uint32_t *)RAM_START; ram_ptr < (uint32_t *)RAM_END; ram_ptr++) {
        uint32_t data;

        if (flash_read(flash_dev, offset, &data, sizeof(uint32_t)) != 0) {
            printk("Flash read failed at offset 0x%08X\n", offset);
            return -1;
        }
        printk("Read %d from FLASH 0x%08X to RAM %p\n", data, offset, ram_ptr);
        *ram_ptr = data;
        offset += sizeof(uint32_t);
    }
    return 0;
}

void checkpoint_test_flash() {
    checkpoint_create();
    printk("\n");
    checkpoint_recover();
    printk("\n");
    printk("DONE\n");
}