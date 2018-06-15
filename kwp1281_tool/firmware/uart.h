#ifndef UART_H
#define UART_H

#include "main.h"
#include <stdint.h>

#define UART_UBRR_115200  (F_CPU/16/(115200-1))
#define UART_UBRR_10400   (F_CPU/16/(10400-1))
#define UART_UBRR_9600    (F_CPU/16/(9600-1))

typedef enum {
    UART0 = 0,
    UART1 = 1,
} uart_num_t;

typedef enum {
    UART_NOT_READY = 0,
    UART_READY = 1,
} uart_status_t;

typedef struct
{
    uint8_t data[256];
    uint8_t write_index;
    uint8_t read_index;
} uart_ringbuffer_t;

void uart_init(uart_num_t uartnum, uint32_t baud);
void uart_flush_tx(uart_num_t uartnum);
void uart_put(uart_num_t uartnum, uint8_t c);
void uart_put16(uart_num_t uartnum, uint16_t w);
void uart_puts(uart_num_t uartnum, char *str);
void uart_puthex(uart_num_t uartnum, uint8_t c);
void uart_puthex16(uart_num_t uartnum, uint16_t w);
uart_status_t uart_rx_ready(uart_num_t uartnum);
void uart_blocking_put(uart_num_t uartnum, uint8_t c);
uint8_t uart_blocking_get(uart_num_t uartnum);
uart_status_t uart_blocking_get_with_timeout(uart_num_t uartnum, uint16_t timeout_ms, uint8_t *rx_byte_out);

#endif
