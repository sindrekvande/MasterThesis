#include "bt.h"
#include "saadc.h"

struct bt_conn *current_conn;

struct bt_conn_cb bluetooth_callbacks = {
	.connected 		= on_connected,
	.disconnected 	= on_disconnected,
};

struct bt_remote_service_cb remote_service_callbacks = {
    .notif_changed = on_notif_changed,
};

/* Callbacks */

void on_connected(struct bt_conn *conn, uint8_t err) {
	if(err) {
		printk("connection err: %d\n", err);
		return;
	}
	//printk("Connected.\n");
	current_conn = bt_conn_ref(conn);
}

void on_disconnected(struct bt_conn *conn, uint8_t reason) {
	//printk("Disconnected (reason: %d)\n", reason);
	if(current_conn) {
		bt_conn_unref(current_conn);
		current_conn = NULL;
	}
}

void on_notif_changed(enum bt_saadc_notifications_enabled status) {
    if (status == BT_SAADC_NOTIFICATIONS_ENABLED) {
        printk("Notifications enabled\n");
        notif_flag = 1;
    } else {
        printk("Notifications disabled\n");
        notif_flag = 0;
    }
}

void communicate_handler(void) {
    printk("Communicate handler\n");
    int err;
    communicate_pd += 1;

    if (!current_conn) {
        printk("No active connection to send notification.\n");
        return;
    }
    communicate_samples[0] = 0xFFFF;
    communicate_samples[1] = checkpoint_pd;
    communicate_samples[2] = recover_pd;
    communicate_samples[3] = measure_pd;
    communicate_samples[4] = communicate_pd;

    uint8_t data_to_send[10*sizeof(uint16_t)]; // changes to uint8_t to receive data in right order

    printk("Saadc notification sending\n");
    for (int i = 0; i < ((NUM_SAMPLES*SAMPLE_SIZE)/10 + (((NUM_SAMPLES*SAMPLE_SIZE)%10) ? 1 : 0)); ++i) {
        memset(data_to_send, 0, sizeof(data_to_send)); // Clear buffer
        for (int j = 0; j < 10; ++j) {
            memcpy(&data_to_send[j*sizeof(uint16_t)], &communicate_samples[(i*10)+j], sizeof(uint16_t));
        }
        //printk("Saadc notification sending\n");
        err = send_saadc_notification(current_conn, data_to_send, sizeof(data_to_send));
        if (err) {
            printk("Failed to send SAADC notification (Error: %d)\n", err);
        }
    }
    printk("Saadc notification sent\n");
}

int advertisment_uninit(void) {
    printk("Unitializing advertisement\n");
    if (current_conn) {
        int err = bt_conn_disconnect(current_conn, BT_HCI_ERR_REMOTE_USER_TERM_CONN);
        if (err) {
            printk("Disconnection failed (err %d)\n", err);
        }

        bt_conn_unref(current_conn);
        current_conn = NULL;
    }

    int err = bt_le_adv_stop();
    if (err) {
        printk("Stopping advertising failed (err %d)\n", err);
    }
    printk("Advertisement unitialized\n");
    return err;
}