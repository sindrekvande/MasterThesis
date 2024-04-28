#ifndef LPCOMP_H
#define LPCOMP_H

#include <nrfx_lpcomp.h>

/** @brief Initializes the LPCOMP component. **/
void lpcomp_wakeup_init(void);

/** @brief Handles LPCOMP events. **/
void lpcomp_event_handler(nrf_lpcomp_event_t event);

#endif