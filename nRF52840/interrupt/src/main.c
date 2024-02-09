/*
 * Copyright (c) 2020 Nordic Semiconductor ASA
 *
 * SPDX-License-Identifier: LicenseRef-Nordic-5-Clause
 */

#include <stdio.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/poweroff.h>

#include <nrfx.h>
#include <hal/nrf_power.h>
#if !NRF_POWER_HAS_RESETREAS
#include <hal/nrf_reset.h>
#endif

#include <dk_buttons_and_leds.h>

#include <hal/nrf_gpio.h>
#include <nrfx_gpiote.h>
#include <stdbool.h>


#define SYSTEM_OFF_DELAY_S	3

#define MAX_REC_COUNT		1
#define NDEF_MSG_BUF_SIZE	128

#define WAKEUP_LED			DK_LED1
#define SYSTEM_ON_LED		DK_LED2

#define SLEEP_BTN			11
#define WAKEUP_BTN			12

static void system_off()
{
	printk("Powering off.\n");

	dk_set_led_off(SYSTEM_ON_LED);
	dk_set_led_off(WAKEUP_LED);

	sys_poweroff();
}

static void input_pin_handle(unsigned int pin, nrfx_gpiote_trigger_t action, void * p)
{
	switch (pin)
	{
	case SLEEP_BTN:
		printk("SLEEP BUTTON\n");
		system_off();
		break;
	
	case WAKEUP_BTN:
		printk("WAKEUP BUTTON\n");
		dk_set_led_on(WAKEUP_LED);
		dk_set_led_on(SYSTEM_ON_LED);
		break;
	}
}


static void gpio_init()
{
	nrfx_err_t err_code; // Hold error value

	if (!nrfx_gpiote_is_init()){
		err_code = nrfx_gpiote_init(NULL); // Initialize the GPIOTE
		printk("Error (0x%X)\n", err_code); 
	}

	nrfx_gpiote_input_config_t in_config;
	in_config.pull = NRF_GPIO_PIN_PULLUP;
	
	nrfx_gpiote_trigger_config_t trig_config;
	trig_config.trigger = NRF_GPIOTE_POLARITY_LOTOHI;

	nrfx_gpiote_handler_config_t hand_config;
	hand_config.handler = &input_pin_handle;

	err_code = nrfx_gpiote_input_configure(SLEEP_BTN, &in_config, &trig_config, &hand_config); // Initialize interrupt pin
	printk("Error (0x%X)\n", err_code);

	// Configuration for WAKEUP_BTN with sense detection
	nrf_gpio_cfg_sense_input(WAKEUP_BTN, NRF_GPIO_PIN_PULLUP, NRF_GPIO_PIN_SENSE_LOW);

	nrfx_gpiote_trigger_enable(SLEEP_BTN, true); // Enable interrupt events
}

/**
 * @brief  Helper function for printing the reason of the last reset.
 * Can be used to confirm that NCF field actually woke up the system.
 */
static void print_reset_reason(void)
{
	uint32_t reas;

#if NRF_POWER_HAS_RESETREAS

	reas = nrf_power_resetreas_get(NRF_POWER);
	nrf_power_resetreas_clear(NRF_POWER, reas);
	if (reas & NRF_POWER_RESETREAS_NFC_MASK) {
		printk("Wake up by NFC field detect\n");
	} else if (reas & NRF_POWER_RESETREAS_RESETPIN_MASK) {
		printk("Reset by pin-reset\n");
	} else if (reas & NRF_POWER_RESETREAS_SREQ_MASK) {
		printk("Reset by soft-reset\n");
	} else if (reas) {
		printk("Reset by a different source (0x%08X)\n", reas);
	} else {
		printk("Power-on-reset\n");
	}

#else

	reas = nrf_reset_resetreas_get(NRF_RESET);
	nrf_reset_resetreas_clear(NRF_RESET, reas);
	if (reas & NRF_RESET_RESETREAS_NFC_MASK) {
		printk("Wake up by NFC field detect\n");
	} else if (reas & NRF_RESET_RESETREAS_RESETPIN_MASK) {
		printk("Reset by pin-reset\n");
	} else if (reas & NRF_RESET_RESETREAS_SREQ_MASK) {
		printk("Reset by soft-reset\n");
	} else if (reas) {
		printk("Reset by a different source (0x%08X)\n", reas);
	} else {
		printk("Power-on-reset\n");
	}

#endif
}

int main(void)
{
	/* Configure LED-pins */
	if (dk_leds_init() < 0) {
		printk("Cannot init LEDs!\n");
		return 0;
	}

	dk_set_led_on(SYSTEM_ON_LED);

	gpio_init();

	print_reset_reason();

	return 0;
}
