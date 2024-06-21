#ifndef LPCOMP_H
#define LPCOMP_H

#include <nrfx_lpcomp.h>

extern int start_flag;

/** @brief Initializes the LPCOMP component. **/
void lpcomp_start_init(void);

/** @brief Handles LPCOMP events. **/
void lpcomp_event_handler(nrf_lpcomp_event_t event);

#endif