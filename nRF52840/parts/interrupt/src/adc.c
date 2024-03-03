#include "adc.h"

int configure_adc(){
    for (size_t i = 0U; i < ARRAY_SIZE(adc_channels); i++) {
        if (!adc_is_ready_dt(&adc_channels[i])) {
            printk("ADC controller device %s not ready\n", adc_channels[i].dev->name);
            return -1;
        }

		err = adc_channel_setup_dt(&adc_channels[i]);
		if (err < 0) {
			printk("Could not setup channel #%d (%d)\n", i, err);
			return -1;
		}
    }
}

int read_adc(){
	for (size_t i = 0U; i < ARRAY_SIZE(adc_channels); i++) {
		int32_t value_mV;

		printk("ADC read - %s, channel %d: ", adc_channels[i].dev->name, adc_channels[i].channel_id);

		(void)adc_sequence_init_dt(&adc_channels[i], &sequence);

		err = adc_read(adc_channels[i].dev, &sequence);
		if (err < 0) {
			printk("Could not read (%d)\n", err);
			return -1;
		}
		/*
		 * If using differential mode, the 16 bit value
		 * in the ADC sample buffer should be a signed 2's
		 * complement value.
		 */
		if (adc_channels[i].channel_cfg.differential) {
			val_mv = (int32_t)((int16_t)buf);
		} else {
			val_mv = (int32_t)buf;
		}
		printk("%"PRId32, value_mV);
		err = adc_raw_to_millivolts_dt(&adc_channels[i],
					       &value_mV);
		/* conversion to mV may not be supported, skip if not */
		if (err < 0) {
			printk(" (value in mV not available)\n");
		} else {
			printk(" = %"PRId32" mV\n", value_mV);
		}
	}
}