#ifndef BT_H
#define BT_H

#include "remote.h"

void on_connected(struct bt_conn *conn, uint8_t err);
void on_disconnected(struct bt_conn *conn, uint8_t reason);
void on_notif_changed(enum bt_saadc_notifications_enabled status);
void fill_saadc_values(void);
void communicate_handler(void);
int advertisment_uninit(void);

extern struct bt_conn_cb bluetooth_callbacks;
extern struct bt_remote_service_cb remote_service_callbacks;

#endif