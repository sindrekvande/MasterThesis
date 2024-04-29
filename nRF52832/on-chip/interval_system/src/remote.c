#include "remote.h"

static K_SEM_DEFINE(bt_init_ok, 0, 1);

#define DEVICE_NAME CONFIG_BT_DEVICE_NAME
#define DEVICE_NAME_LEN (sizeof(DEVICE_NAME)-1)

static uint16_t saadc_value = 0;
static struct bt_remote_service_cb remote_service_callbacks;
enum bt_saadc_notifications_enabled notifications_enabled;

static const struct bt_data ad[] = {
    BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
    BT_DATA(BT_DATA_NAME_COMPLETE, DEVICE_NAME, DEVICE_NAME_LEN)
};

static const struct bt_data sd[] = {
    BT_DATA_BYTES(BT_DATA_UUID128_ALL, BT_UUID_REMOTE_SERV_VAL),
};

/* Declarations */
static ssize_t read_saadc_characteristic_cb(struct bt_conn *conn, const struct bt_gatt_attr *attr, void *buf, uint16_t len, uint16_t offset);
void saadc_chrc_ccc_cfg_changed(const struct bt_gatt_attr *attr, uint16_t value);

BT_GATT_SERVICE_DEFINE(remote_srv,
BT_GATT_PRIMARY_SERVICE(BT_UUID_REMOTE_SERVICE),
    BT_GATT_CHARACTERISTIC(BT_UUID_REMOTE_SAADC_CHRC,
                           BT_GATT_CHRC_READ | BT_GATT_CHRC_NOTIFY,
                           BT_GATT_PERM_READ,
                           read_saadc_characteristic_cb, NULL, NULL),
    BT_GATT_CCC(saadc_chrc_ccc_cfg_changed, BT_GATT_PERM_READ | BT_GATT_PERM_WRITE),
);

/* Callbacks */

void saadc_chrc_ccc_cfg_changed(const struct bt_gatt_attr *attr, uint16_t value) {
    bool notif_enabled = (value == BT_GATT_CCC_NOTIFY);
    printf("Notifications %s\n", notif_enabled? "enabled":"disabled");

    notifications_enabled = notif_enabled? BT_SAADC_NOTIFICATIONS_ENABLED:BT_SAADC_NOTIFICATIONS_DISABLED;

    if (remote_service_callbacks.notif_changed) {
        remote_service_callbacks.notif_changed(notifications_enabled);
    }
}

static ssize_t read_saadc_characteristic_cb(struct bt_conn *conn, const struct bt_gatt_attr *attr, void *buf, uint16_t len, uint16_t offset) {
    return bt_gatt_attr_read(conn, attr, buf, len, offset, &saadc_value, sizeof(saadc_value));
}

void bt_ready(int err) {
    if (err) {
        printf("Bluetooth initialization failed with error %d\n", err);
    } 
    k_sem_give(&bt_init_ok);
}

void on_sent(struct bt_conn *conn, void *user_data) {
    ARG_UNUSED(user_data);
    printf("Notification sent on connection %p\n", (void *)conn);
}

/* Remote controller functions */

int send_saadc_notification(struct bt_conn *conn, uint8_t *values, uint16_t length) {
    int err = 0;
    const struct bt_gatt_attr *attr = &remote_srv.attrs[2];
    err = bt_gatt_notify(conn, attr, values, length);
    return err;
}

void set_saadc_value(uint16_t *values) {
    saadc_value = *values;
}

int bluetooth_init(struct bt_conn_cb *bt_cb, struct bt_remote_service_cb *remote_cb) {
    int err;
    printf("Initializing Bluetooth\n");

    if (bt_cb == NULL || remote_cb == NULL) {
        return NRFX_ERROR_NULL;
    }

    bt_conn_cb_register(bt_cb);
    remote_service_callbacks.notif_changed = remote_cb->notif_changed;

    err = bt_enable(bt_ready);
    if (err) {
        printf("bt_enable returned %d\n", err);
        return err;
    }

    k_sem_take(&bt_init_ok, K_FOREVER);

    return err;
}

int advertisment_init(void) {
    printf("INIT ADVERTISMENT\n");

    const struct bt_le_adv_param adv_param = {
        .options = BT_LE_ADV_OPT_CONNECTABLE,
        .interval_min = BT_GAP_ADV_FAST_INT_MIN_2,
        .interval_max = BT_GAP_ADV_FAST_INT_MAX_2,
    };

    int err = bt_le_adv_start(&adv_param, ad, ARRAY_SIZE(ad), sd, ARRAY_SIZE(sd));
    if (err){
        printf("couldn't start advertising (err = %d)\n", err);
        return err;
    }

    return err;
}