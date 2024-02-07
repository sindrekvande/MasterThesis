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
//#include <hal/nrf_gpiote.h>
#include <nrfx_gpiote.h>
#include <stdbool.h>


#define SYSTEM_OFF_DELAY_S	3

#define MAX_REC_COUNT		1
#define NDEF_MSG_BUF_SIZE	128

#define SLEEP_LED			17
#define SYSTEM_ON_LED		DK_LED2

#define SLEEP_PIN			13
#define WAKEUP_PIN			14


static void input_pin_handle(unsigned int pin, nrfx_gpiote_trigger_t action, void * p)
{
	printk("Handler \n");
	nrf_gpio_pin_toggle(SLEEP_LED); // Toggle LED on interrupt
	
	printk("Powering off.\n");
	dk_set_led_off(SYSTEM_ON_LED);
	sys_poweroff();
}


static void gpio_init()
{
	nrfx_err_t err_code; // Hold error value

	err_code = nrfx_gpiote_init(0); // Initialize the GPIOTE
	printk("Error (0x%X)\n", err_code); // Check for errors

	nrf_gpio_cfg_output(SLEEP_LED); // Initialize the LED
	nrf_gpio_pin_set(SLEEP_LED); // Turn off the LED

	nrfx_gpiote_input_config_t in_config;
	in_config.pull = NRF_GPIO_PIN_PULLUP;
	
	nrfx_gpiote_trigger_config_t trig_config;
	trig_config.trigger = NRF_GPIOTE_POLARITY_HITOLO;

	nrfx_gpiote_handler_config_t hand_config;
	hand_config.handler = &input_pin_handle;

	err_code = nrfx_gpiote_input_configure(SLEEP_PIN, &in_config, &trig_config, &hand_config); // Initialize interrupt pin
	printk("Error (0x%X)\n", err_code);;

	nrfx_gpiote_trigger_enable(SLEEP_PIN, true); // Enable interrupt events
}

static void system_off()
{
	printk("Powering off.\n");

	dk_set_led_off(SYSTEM_ON_LED);

	sys_poweroff();
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

	while (true)
	{

	}
}
