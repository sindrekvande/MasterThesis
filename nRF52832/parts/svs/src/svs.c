#include <nrfx_power.h>
#include "svs.h"
#include <stdio.h>

void svs_init() {
    printf("SVS INIT\n");

    nrfx_power_pofwarn_config_t pof_config = {
        .thr = NRF_POWER_POFTHR_V18,
        .handler = svs_handler
    };

    nrfx_power_pof_init(&pof_config);

    nrfx_power_pof_enable(&pof_config);
}

void svs_handler() {
    printf("SVS HANDLER\n");
}