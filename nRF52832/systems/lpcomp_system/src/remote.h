#ifndef REMOTE_H
#define REMOTE_H

#include <zephyr/kernel.h>

#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/uuid.h>
#include <zephyr/bluetooth/gatt.h>
#include <zephyr/bluetooth/hci.h>

/** @brief UUID of the Remote Service. **/
#define BT_UUID_REMOTE_SERV_VAL \
	BT_UUID_128_ENCODE(0xe9ea0001, 0xe19b, 0x482d, 0x9293, 0xc7907585fc48)

/** @brief UUID of the SAADC Characteristic. **/
#define BT_UUID_REMOTE_SAADC_CHRC_VAL \
	BT_UUID_128_ENCODE(0xe9ea0002, 0xe19b, 0x482d, 0x9293, 0xc7907585fc48)

#define BT_UUID_REMOTE_SERVICE          BT_UUID_DECLARE_128(BT_UUID_REMOTE_SERV_VAL)
#define BT_UUID_REMOTE_SAADC_CHRC 		BT_UUID_DECLARE_128(BT_UUID_REMOTE_SAADC_CHRC_VAL)

enum bt_saadc_notifications_enabled {
	BT_SAADC_NOTIFICATIONS_ENABLED,
	BT_SAADC_NOTIFICATIONS_DISABLED,
};

struct bt_remote_service_cb {
	void (*notif_changed)(enum bt_saadc_notifications_enabled status);
};

int send_saadc_notification(struct bt_conn *conn, uint32_t value, uint16_t length);
void set_saadc_value(uint32_t adc_value);
int bluetooth_init(struct bt_conn_cb *bt_cb, struct bt_remote_service_cb *remote_cb);
int advertisment_init(void); 

#endif