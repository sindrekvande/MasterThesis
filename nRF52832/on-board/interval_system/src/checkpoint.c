#include "checkpoint.h"
#include "saadc.h"

const struct device *flash_dev = PARTITION_DEVICE;
uint32_t checkpoint_data[CHECKPOINT_WORDS] = {0};
uint32_t first_boot_flag;

bool check_first_boot() {
    if (flash_read(flash_dev, FIRST_BOOT_FLAG_ADDR, &first_boot_flag, sizeof(first_boot_flag)) != 0) {
        printk("Flash read failed at first boot check.\n");
        return false;
    }
    if (first_boot_flag == FIRST_BOOT_FLAG_VALUE) {
        return false;
    } else {
        return true;
    }
    return false;
}

bool set_first_boot_flag() {
    uint32_t first_boot_flag_value = 0xA5A5A5A5;
    if (first_boot_flag != FIRST_BOOT_FLAG_VALUE) {
        if (flash_erase(flash_dev, FIRST_BOOT_FLAG_ADDR, FLASH_PAGE_SIZE) != 0) {
            printk("Flash erase failed during first boot flag set.\n");
            return false;
        }
        if (flash_write(flash_dev, FIRST_BOOT_FLAG_ADDR, &first_boot_flag_value, sizeof(FIRST_BOOT_FLAG_VALUE)) != 0) {
            printk("Flash write failed during first boot flag set.\n");
            return false;
        }
        printk("First boot detected and flag set.\n");
        return true;
    }
    return false;
}

int checkpoint_create() {
    printk("#### CREATING CHECKPOINT ###\n");
    checkpoint_pd += 1; // SIMPLIFIED SOLUTION
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
    }
    //return save_ram_to_flash(); // FULL SOLUTION
    return 0; // SIMPLIFIED SOLUTION
}

int checkpoint_recover() {
    printk("#### RECOVERING CHECKPOINT ####\n");
    uint32_t offset = PARTITION_OFFSET;

    for (uint32_t i = 0; i < CHECKPOINT_WORDS; i++) {
		if (flash_read(flash_dev, offset + (i * sizeof(uint32_t)), &checkpoint_data[i], sizeof(checkpoint_data[i])) != 0) {
			printk("Flash read failed at offset 0x%08X\n", offset + (i * sizeof(uint32_t)));
			return -1;
		}
    }
    set_program_state(checkpoint_data);
    //return retrieve_ram_from_flash(); // FULL SOLUTION
    return 0; // SIMPLIFIED SOLUTION
}

void get_program_state(uint32_t * buf) { // Number of stored values needs to match CHECKPOINT_WORDS
    printk("#### GET PROGRAM STATE ####\n");

    buf[0] = next_state; 
    buf[1] = current_sample; 

    // --- PERFORMANCE DATA - SHOULD BE EXCLUDED FROM RESULTS --- //
    buf[2] = checkpoint_pd;
    buf[3] = recover_pd;
    buf[4] = communicate_pd;
    buf[5] = measure_pd;
    // ---------------------------------------------------------- //

    uint16_t data_index = 6; 
    for (int i = 0; i < NUM_SAMPLES*SAMPLE_SIZE; ++i) {
        buf[data_index] = communicate_samples[i];
        data_index += 1;
    }

    // FULL SOLUTION //
    //__asm__ volatile("MOV %0, R0" : "=r" (buf[0]) : : );
    //__asm__ volatile("MOV %0, R1" : "=r" (buf[1]) : : );
    //__asm__ volatile("MOV %0, R2" : "=r" (buf[2]) : : );
    //__asm__ volatile("MOV %0, R3" : "=r" (buf[3]) : : );
    //__asm__ volatile("MOV %0, R4" : "=r" (buf[4]) : : );
    //__asm__ volatile("MOV %0, R5" : "=r" (buf[5]) : : );
    //__asm__ volatile("MOV %0, R6" : "=r" (buf[6]) : : );
    //__asm__ volatile("MOV %0, R7" : "=r" (buf[7]) : : );
    //__asm__ volatile("MOV %0, R8" : "=r" (buf[8]) : : );
    //__asm__ volatile("MOV %0, R9" : "=r" (buf[9]) : : );
    //__asm__ volatile("MOV %0, R10" : "=r" (buf[10]) : : );
    //__asm__ volatile("MOV %0, R11" : "=r" (buf[11]) : : );
    //__asm__ volatile("MOV %0, R12" : "=r" (buf[12]) : : );

    //__asm__ volatile("MRS %0, MSP\n": "=r" (buf[13]) : : );
    //__asm__ volatile("MRS %0, PSP\n": "=r" (buf[14]) : : );
    //__asm__ volatile("MOV %0, LR\n": "=r" (buf[15]) : : );
    //__asm__ volatile("MOV %0, PC\n": "=r" (buf[16]) : : );
}

void set_program_state(uint32_t * buf) {
    printk("#### SET PROGRAM STATE ####\n");

    recover_pd += 1; // SIMPLIFIED SOLUTION

    next_state = buf[0];
    current_sample = buf[1];
    //next_state = 0;
    //current_sample = 0;

    // --- PERFORMANCE DATA - SHOULD BE EXCLUDED FROM RESULTS --- //
    checkpoint_pd = buf[2];
    recover_pd = buf[3];
    communicate_pd = buf[4];
    measure_pd = buf[5];
    // ---------------------------------------------------------- //

    uint16_t data_index = 6;
    for (int i = 0; i < NUM_SAMPLES*SAMPLE_SIZE; ++i) {
        communicate_samples[i] = buf[data_index];
        data_index += 1;
    }

    // FULL SOLUTION //
    //__asm__ volatile("MOV R0, %0" : : "r" (buf[0]) : );
    //__asm__ volatile("MOV R1, %0" : : "r" (buf[1]) : );
    //__asm__ volatile("MOV R2, %0" : : "r" (buf[2]) : );
    //__asm__ volatile("MOV R3, %0" : : "r" (buf[3]) : );
    //__asm__ volatile("MOV R4, %0" : : "r" (buf[4]) : );
    //__asm__ volatile("MOV R5, %0" : : "r" (buf[5]) : );
    //__asm__ volatile("MOV R6, %0" : : "r" (buf[6]) : );
    //__asm__ volatile("MOV R7, %0" : : "r" (buf[7]) : );
    //__asm__ volatile("MOV R8, %0" : : "r" (buf[8]) : );
    //__asm__ volatile("MOV R9, %0" : : "r" (buf[9]) : );
    //__asm__ volatile("MOV R10, %0" : : "r" (buf[10]) : );
    //__asm__ volatile("MOV R11, %0" : : "r" (buf[11]) : );
    //__asm__ volatile("MOV R12, %0" : : "r" (buf[12]) : );

    //__asm__ volatile("MSR MSP, %0\n": : "r" (buf[13]) : );
    //__asm__ volatile("MSR PSP, %0\n": : "r" (buf[14]) : ); // This recover does not work for nRF52840, sometimes?
    //__asm__ volatile("MOV LR, %0\n": : "r" (buf[15]) : ); // This recover does not work for nRF52832, sometimes?
    //__asm__ volatile("MOV PC, %0\n": : "r" (buf[16]) : );
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
        offset += sizeof(uint32_t);
    }
    checkpoint_pd += 1;
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
        *ram_ptr = data;
        offset += sizeof(uint32_t);
    }
    recover_pd += 1;
    return 0;
}