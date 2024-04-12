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
		printf("connection err: %d\n", err);
		return;
	}
	printf("Connected.\n");
	current_conn = bt_conn_ref(conn);
}

void on_disconnected(struct bt_conn *conn, uint8_t reason) {
	printf("Disconnected (reason: %d)\n", reason);
	if(current_conn) {
		bt_conn_unref(current_conn);
		current_conn = NULL;
	}
}

void on_notif_changed(enum bt_saadc_notifications_enabled status) {
    if (status == BT_SAADC_NOTIFICATIONS_ENABLED) {
        printf("Notifications enabled\n");
    } else {
        printf("Notifications disabled\n");
    }
}

void communicate_handler(void) {
    int err;

    if (!current_conn) {
        printf("No active connection to send notification.\n");
        return;
    }

    for (int i = 0; i < NUM_SAMPLES; ++i) {
        for (int j = 0; j < SAMPLE_SIZE; ++j) {
            float value = communicate_samples[i][j] * 100; 
            uint32_t value_int = (uint32_t)value;
            //printf("Sending sample %d: %d\n", i, value_int);
            set_saadc_value(value_int);
            err = send_saadc_notification(current_conn, value_int, sizeof(value_int));
            if (err) {
                printf("Failed to send SAADC notification (Error: %d)\n", err);
            }
            k_sleep(K_MSEC(50));
        }
    }
}

int advertisment_uninit(void) {
    printf("UNINIT ADVERTISMENT\n");

    if (current_conn) {
        int err = bt_conn_disconnect(current_conn, BT_HCI_ERR_REMOTE_USER_TERM_CONN);
        if (err) {
            printf("Disconnection failed (err %d)\n", err);
        }

        bt_conn_unref(current_conn);
        current_conn = NULL;
    }

    int err = bt_le_adv_stop();
    if (err) {
        printf("Stopping advertising failed (err %d)\n", err);
    }
    return err;
}