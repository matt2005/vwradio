/* Pin  3: PB2 STB from radio in
 * Pin  4: PB3 /SS out (software generated, connect to PB4)
 * Pin  5: PB4 /SS in (connect to PB3)
 * Pin  6: PB5 MOSI (to radio's DAT)
 * Pin  7: PB6 MISO (not connected for now)
 * pin  8: PB7 SCK (to radio's CLK)
 * Pin 11: GND
 * Pin 14: PD0/RXD (to PC's serial TXD)
 * Pin 15: PD1/TXD (to PC's serial RXD)
 * Pin 18: PD4: Green LED
 * Pin 19: PD5: Red LED
 */

#ifndef F_CPU
#define F_CPU 20000000UL
#endif

#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/atomic.h>
#include <util/delay.h>
#define BAUD 115200
#include <util/setbaud.h>
#include <string.h>

#define LED_PORT PORTD
#define LED_DDR DDRD
#define LED_RED PD6
#define LED_GREEN PD5

/*************************************************************************
 * LED
 *************************************************************************/

void led_init()
{
    LED_DDR = _BV(LED_GREEN) | _BV(LED_RED);
    LED_PORT = 0;
}

void led_set(uint8_t lednum, uint8_t state)
{
    if (state)
    {
        LED_PORT |= _BV(lednum);
    }
    else
    {
        LED_PORT &= ~_BV(lednum);
    }
}

void led_blink(uint8_t lednum, uint16_t times)
{
    while (times > 0)
    {
        led_set(lednum, 1);
        _delay_ms(250);
        led_set(lednum, 0);
        _delay_ms(250);
        times -= 1;
    }
}

/*************************************************************************
 * Ring Buffers for UART
 *************************************************************************/

typedef struct
{
    uint8_t data[256];
    uint8_t write_index;
    uint8_t read_index;
} ringbuffer_t;

void buf_init(volatile ringbuffer_t *buf)
{
    buf->read_index = 0;
    buf->write_index = 0;
}

void buf_write_byte(volatile ringbuffer_t *buf, uint8_t c)
{
    buf->data[buf->write_index++] = c;
}

uint8_t buf_read_byte(volatile ringbuffer_t *buf)
{
    uint8_t c = buf->data[buf->read_index++];
    return c;
}

uint8_t buf_has_byte(volatile ringbuffer_t *buf)
{
    return buf->read_index != buf->write_index;
}

/*************************************************************************
 * UART
 *************************************************************************/

volatile ringbuffer_t uart_rx_buffer;
volatile ringbuffer_t uart_tx_buffer;

void uart_init()
{
    // Baud Rate
    UBRR0H = UBRRH_VALUE;
    UBRR0L = UBRRL_VALUE;
#if USE_2X
    UCSR0A |= _BV(U2X0);
#else
    UCSR0A &= ~(_BV(U2X0));
#endif

    UCSR0C = _BV(UCSZ01) | _BV(UCSZ00); // N-8-1
    UCSR0B = _BV(RXEN0) | _BV(TXEN0);   // Enable RX and TX
    // Enable the USART Recieve Complete
    UCSR0B |= _BV(RXCIE0);

    buf_init(&uart_rx_buffer);
    buf_init(&uart_tx_buffer);
}

void uart_flush_tx()
{
    while (buf_has_byte(&uart_tx_buffer)) {}
}

void uart_putc(uint8_t c)
{
    buf_write_byte(&uart_tx_buffer, c);
    // Enable UDRE interrupts
    UCSR0B |= _BV(UDRIE0);
}

void uart_puts(uint8_t *str)
{
    while (*str != '\0')
    {
        uart_putc(*str);
        str++;
    }
}

void uart_puthex_nib(uint8_t c)
{
    if (c < 10) // 0-9
    {
        uart_putc(c + 0x30);
    }
    else // A-F
    {
        uart_putc(c + 0x37);
    }
}

void uart_puthex_byte(uint8_t c)
{
    uart_puthex_nib((c & 0xf0) >> 4);
    uart_puthex_nib(c & 0x0f);
}

void uart_puthex_16(uint16_t w)
{
    uart_puthex_byte((w & 0xff00) >> 8);
    uart_puthex_byte((w & 0x00ff));
}

// USART Receive Complete
ISR(USART0_RX_vect)
{
    uint8_t c;
    c = UDR0;
    buf_write_byte(&uart_rx_buffer, c);
}

// USART Data Register Empty (USART is ready to transmit a byte)
ISR(USART0_UDRE_vect)
{
    if (uart_tx_buffer.read_index != uart_tx_buffer.write_index)
    {
        UDR0 = uart_tx_buffer.data[uart_tx_buffer.read_index++];
    }
    else
    {
        // Disable UDRE interrupts
        UCSR0B &= ~_BV(UDRE0);
    }
}

/*************************************************************************
 * SPI Slave interface to Radio
 *************************************************************************/

// buffer for current SPI transfer in process
volatile uint16_t spi_slave_data[32];
volatile uint16_t spi_slave_data_index;

// upd16432b command request
typedef struct
{
    uint8_t data[32]; // spi bytes
    uint8_t size;
} upd_command_t;
// circular buffer for receiving upd commands
volatile upd_command_t upd_cmds_buf[256];
volatile uint8_t upd_cmds_buf_write_index;
volatile uint8_t upd_cmds_buf_read_index;

void spi_slave_init()
{
    uint8_t upd_cmds_buf_read_index = 0;
    uint8_t upd_cmds_buf_write_index = 0;

    spi_slave_data_index = 0;

    // PB2 as input (STB from radio)
    DDRB &= ~_BV(PB2);
    // PB3 as output (/SS output we'll make in software from STB)
    DDRB |= _BV(PB3);
    // PB3 state initially high (/SS not asserted)
    PORTB |= _BV(PB3);
    // Set pin change enable mask 1 for PB2 (PCINT10) only
    PCMSK1 = _BV(PCINT10);
    // Any transition generates the pin change interrupt
    EICRA = _BV(ISC11);
    // Enable interrupts from pin change group 1 only
    PCICR = _BV(PCIE1);

    // PB4 as input (AVR hardware SPI /SS input)
    DDRB &= ~_BV(PB4);
    // PB5 as input (AVR hardware SPI MOSI)
    DDRB &= ~_BV(PB5);

    // SPI data output register initially 0
    SPDR = 0;

    // SPE=1 SPI enabled, MSTR=0 SPI slave,
    // DORD=0 MSB first, CPOL=1, CPHA=1
    // SPIE=1 SPI interrupts enabled
    SPCR = _BV(SPE) | _BV(CPOL) | _BV(CPHA) | _BV(SPIE);
}

// When STB from radio changes, set /SS output to inverse of STB.
ISR(PCINT1_vect)
{
    if (PINB & _BV(PB2)) // STB=high
    {
        PORTB &= ~_BV(PB3); // /SS=low
        spi_slave_data_index = 0;
    }
    else // STB=low
    {
        PORTB |= _BV(PB3); // /SS=high

        // transfer complete

        // empty data can occur if we miss a strobe edge
        // or if we are strobed but no spi bytes are received
        if (spi_slave_data_index != 0)
        {
            // key data request
            if (spi_slave_data[0] == 0x44)
            {
                // ignored for now
            }

            // command to move into the circular buffer
            else
            {
                volatile upd_command_t *cmd;
                cmd = &upd_cmds_buf[upd_cmds_buf_write_index];

                uint8_t i;
                for (i=spi_slave_data_index-1; i!=0xff; i--)
                {
                    cmd->data[i] = spi_slave_data[i];
                }
                cmd->size = spi_slave_data_index;

                upd_cmds_buf_write_index++;
            }
        }
    }
}

// SPI Serial Transfer Complete
ISR(SPI_STC_vect)
{
    spi_slave_data[spi_slave_data_index++] = SPDR;
}

/*************************************************************************
 * NEC uPD16432B LCD Controller Emulator
 *************************************************************************/

// Selected RAM area
#define UPD_RAM_DISPLAY_DATA 0
#define UPD_RAM_PICTOGRAPH 1
#define UPD_RAM_CHARGEN 2
#define UPD_RAM_NONE 0xFF
// Address increment mode
#define UPD_INCREMENT_OFF 0
#define UPD_INCREMENT_ON 1
// RAM sizes
#define UPD_DISPLAY_DATA_RAM_SIZE 0x19
#define UPD_PICTOGRAPH_RAM_SIZE 0x08
#define UPD_CHARGEN_RAM_SIZE 0x70

typedef struct
{
    uint8_t ram_area;  // Selected RAM area
    uint8_t ram_size;  // Size of selected RAM area
    uint8_t address;   // Current address in that area
    uint8_t increment; // Address increment mode on/off

    uint8_t display_data_ram[UPD_DISPLAY_DATA_RAM_SIZE];
    uint8_t pictograph_ram[UPD_PICTOGRAPH_RAM_SIZE];
    uint8_t chargen_ram[UPD_CHARGEN_RAM_SIZE];
} upd_state_t;

upd_state_t upd_state;

void upd_init()
{
    uint8_t i;
    for (i=0; i<UPD_DISPLAY_DATA_RAM_SIZE; i++)
    {
        upd_state.display_data_ram[i] = 0;
    }
    for (i=0; i<UPD_PICTOGRAPH_RAM_SIZE; i++)
    {
        upd_state.pictograph_ram[i] = 0;
    }
    for (i=0; i<UPD_CHARGEN_RAM_SIZE; i++)
    {
        upd_state.chargen_ram[i] = 0;
    }
    upd_state.ram_area = UPD_RAM_NONE;
    upd_state.ram_size = 0;
    upd_state.address = 0;
    upd_state.increment = UPD_INCREMENT_OFF;
}

void _upd_wrap_address()
{
    if (upd_state.address >= upd_state.ram_size)
    {
        upd_state.address = 0;
    }
}

void _upd_write_data_byte(uint8_t b)
{
    switch (upd_state.ram_area)
    {
        case UPD_RAM_DISPLAY_DATA:
            upd_state.display_data_ram[upd_state.address] = b;
            break;

        case UPD_RAM_PICTOGRAPH:
            upd_state.pictograph_ram[upd_state.address] = b;
            break;

        case UPD_RAM_CHARGEN:
            upd_state.chargen_ram[upd_state.address] = b;
            break;

        case UPD_RAM_NONE:
        default:
            return;
    }

    if (upd_state.increment == UPD_INCREMENT_ON)
    {
        upd_state.address++;
        _upd_wrap_address();
    }
}

void _upd_process_address_setting_cmd(uint8_t cmd)
{
    uint8_t address;
    address = cmd & 0b00011111;

    switch (upd_state.ram_area)
    {
        case UPD_RAM_DISPLAY_DATA:
        case UPD_RAM_PICTOGRAPH:
            upd_state.address = address;
            _upd_wrap_address();
            break;

        case UPD_RAM_CHARGEN:
            // for chargen, address is character number (valid from 0 to 0x0F)
            if (address < 0x10)
            {
                upd_state.address = address * 7; // 7 bytes per character
            }
            else
            {
                upd_state.address = 0;
            }
            break;

        case UPD_RAM_NONE:
        default:
            address = 0;
            break;
    }
}

void _upd_process_data_setting_cmd(uint8_t cmd)
{
    uint8_t mode;
    mode = cmd & 0b00000111;

    // set ram target area
    switch (mode)
    {
        case UPD_RAM_DISPLAY_DATA:
            upd_state.ram_area = UPD_RAM_DISPLAY_DATA;
            upd_state.ram_size = UPD_DISPLAY_DATA_RAM_SIZE;
            // TODO does the real uPD16432B reset the address?
            break;

        case UPD_RAM_PICTOGRAPH:
            upd_state.ram_area = UPD_RAM_PICTOGRAPH;
            upd_state.ram_size = UPD_PICTOGRAPH_RAM_SIZE;
            // TODO does the real uPD16432B reset the address?
            break;

        case UPD_RAM_CHARGEN:
            upd_state.ram_area = UPD_RAM_CHARGEN;
            upd_state.ram_size = UPD_CHARGEN_RAM_SIZE;
            // TODO does the real uPD16432B reset the address?
            break;

        case UPD_RAM_NONE:
        default:
            upd_state.ram_area = UPD_RAM_NONE;
            upd_state.ram_size = 0;
            upd_state.address = 0;
    }

    // set increment mode
    switch (mode)
    {
        // only these modes support setting increment on/off
        case UPD_RAM_DISPLAY_DATA:
        case UPD_RAM_PICTOGRAPH:
            upd_state.increment = ((cmd & 0b00001000) == 0);
            break;

        // other modes always increment and also reset address
        default:
            upd_state.increment = 1;
            upd_state.address = 0;
            break;
    }

    // TODO changing data mode may make current address out of bounds
    // what does the real uPD16432B do when data setting is changed?
    _upd_wrap_address();
}

void upd_process_command(upd_command_t *updcmd)
{
    // No bytes SPI were received while STB was asserted
    if (updcmd->size == 0)
    {
        return;
    }

    // Process command byte
    uint8_t cmd;
    cmd = updcmd->data[0];
    switch (cmd & 0b11000000)
    {
        case 0b01000000:
            _upd_process_data_setting_cmd(cmd);
            break;

        case 0b10000000:
            _upd_process_address_setting_cmd(cmd);
            break;

        default:
            break;
    }

    // Process data bytes
    if ((upd_state.ram_area != UPD_RAM_NONE) && (updcmd->size > 1))
    {
        uint8_t i;
        for (i=1; i<updcmd->size; i++)
        {
            _upd_write_data_byte(updcmd->data[i]);
        }
    }
}

/*************************************************************************
 * Command Interpreter
 *************************************************************************/

uint8_t cmd_buf[256];
uint8_t cmd_buf_index;
uint8_t cmd_expected_length;

#define ACK 0x06
#define NAK 0x15

#define CMD_SET_LED 0x01
#define CMD_ECHO 0x02
#define CMD_DUMP_UPD_STATE 0x03
#define CMD_RESET_UPD 0x04
#define CMD_PROCESS_UPD_COMMAND 0x05
#define CMD_ARG_GREEN_LED 0x00
#define CMD_ARG_RED_LED 0x01

void cmd_init()
{
    cmd_buf_index = 0;
    cmd_expected_length = 0;
}

/* Start or restart the command timeout timer.
 * Call this after each byte of the command is received.
 */
void cmd_timer_start()
{
    // set timer1 CTC mode (CS11=0, CS10=1 = prescaler 1024)
    TCCR1B = (1 << CS12) | (0 << CS11) | (1 << CS10);

    // set compare value (2 seconds at 18.432MHz with prescaler 1024)
    OCR1A = 39062;

    // set initial count
    TCNT1 = 0;

    // enable timer1 compare interrupt
    TIMSK1 = (1 << OCIE1A);
}

/* Stop the command timeout timer.
 * Call this after the last byte of a command has been received.
 */
void cmd_timer_stop()
{
    // stop timer1
    TCCR1B = 0;
    // disable timer1 compare interrupt
    TIMSK1 = 0;
}

/* Command timeout has occurred while receiving command bytes.  We forget the
 * buffer and don't send any reply.  This allows the client to resynchronize
 * by waiting longer than the timeout.
 */
ISR(TIMER1_COMPA_vect)
{
    cmd_timer_stop();
    cmd_init();
}

void cmd_reply_ack()
{
    uart_putc(0x01); // 1 byte to follow
    uart_putc(ACK);  // ACK byte
    uart_flush_tx();
}

void cmd_reply_nak()
{
    uart_putc(0x01); // 1 byte to follow
    uart_putc(NAK);  // NAK byte
    uart_flush_tx();
}

/* Command: Reset uPD16432B Emulator
 * Arguments: none
 * Returns: <ack>
 *
 * Reset the uPD16432B Emulator to its default state
 */
void cmd_do_reset_upd()
{
    if (cmd_buf_index != 1)
    {
        cmd_reply_nak();
        return;
    }

    upd_init();
    cmd_reply_ack();
}

/* Command: Dump uPD16432B Emulator State
 * Arguments: none
 * Returns: <ack> <all bytes in upd_state>
 *
 * Dumps the current state of the uPD16432B Emulator.
 */
void cmd_do_dump_upd_state()
{
    if (cmd_buf_index != 1)
    {
        cmd_reply_nak();
        return;
    }

    uint8_t size = 1 + // ACK byte
                   1 + // Selected RAM area
                   1 + // Size of selected RAM area
                   1 + // Current address in that area
                   1 + // Address increment mode on/off
                   UPD_DISPLAY_DATA_RAM_SIZE +
                   UPD_PICTOGRAPH_RAM_SIZE +
                   UPD_CHARGEN_RAM_SIZE;

    uart_putc(size); // number of bytes to follow
    uart_putc(ACK); // ACK byte
    uart_putc(upd_state.ram_area);
    uart_putc(upd_state.ram_size);
    uart_putc(upd_state.address);
    uart_putc(upd_state.increment);
    uart_flush_tx();
    uint8_t i;
    for (i=0; i<UPD_DISPLAY_DATA_RAM_SIZE; i++)
    {
        uart_putc(upd_state.display_data_ram[i]);
    }
    uart_flush_tx();
    for (i=0; i<UPD_PICTOGRAPH_RAM_SIZE; i++)
    {
        uart_putc(upd_state.pictograph_ram[i]);
    }
    uart_flush_tx();
    for (i=0; i<UPD_CHARGEN_RAM_SIZE; i++)
    {
        uart_putc(upd_state.chargen_ram[i]);
    }
    uart_flush_tx();
}

/* Command: Process uPD16432B Emulator Command
 * Arguments: <cmd byte> <cmd arg byte1> <cmd arg byte2> ...
 * Returns: <ack>
 *
 * Sends a fake SPI command to the uPD16432B Emulator.  The
 * arguments are the SPI bytes that would be received by the uPD16432B
 * while it is selected with STB high.
 */
void cmd_do_process_upd_command()
{
    upd_command_t cmd;

    uint8_t i;
    for (i=1; i<cmd_buf_index; i++)
    {
        cmd.data[i-1] = cmd_buf[i];
    }
    cmd.size = i-1;

    upd_process_command(&cmd);
    return cmd_reply_ack();
}

/* Command: Echo
 * Arguments: <arg1> <arg2> <arg3> ...
 * Returns: <ack> <arg1> <arg1> <arg3> ...
 *
 * Echoes the arguments received back to the client.  If no args were
 * received after the command byte, an empty ACK response is returned.
 */
void cmd_do_echo()
{
    uart_putc(cmd_buf_index); // number of bytes to follow
    uart_putc(ACK); // ACK byte
    uint8_t i;
    for (i=1; i<cmd_buf_index; i++)
    {
        uart_putc(cmd_buf[i]);
        uart_flush_tx();
    }
}

/* Command: Set LED
 * Arguments: <led number> <led state>
 * Returns: <ack|nak>
 *
 * Turns one of the LEDs on or off.  Returns a NAK if the LED
 * number is not recognized.
 */
void cmd_do_set_led()
{
    if (cmd_buf_index != 3)
    {
        cmd_reply_nak();
        return;
    }

    uint8_t led_num = cmd_buf[1];
    uint8_t led_state = cmd_buf[2];

    if (led_num == CMD_ARG_RED_LED)
    {
        led_set(LED_RED, led_state);
    }
    else if (led_num == CMD_ARG_GREEN_LED)
    {
        led_set(LED_GREEN, led_state);
    }
    else
    {
        cmd_reply_nak();
        return;
    }

    cmd_reply_ack();
}

/* Dispatch a command.  A complete command packet has been received.  The
 * command buffer has one more bytes.  The first byte is the command byte.
 * Dispatch to a handler, or return a NAK if the command is unrecognized.
 */
void cmd_dispatch()
{
    switch (cmd_buf[0])
    {
        case CMD_SET_LED:
            cmd_do_set_led();
            break;
        case CMD_ECHO:
            cmd_do_echo();
            break;
        case CMD_DUMP_UPD_STATE:
            cmd_do_dump_upd_state();
            break;
        case CMD_RESET_UPD:
            cmd_do_reset_upd();
            break;
        case CMD_PROCESS_UPD_COMMAND:
            cmd_do_process_upd_command();
            break;
        default:
            cmd_reply_nak();
    }
}

/* Receive a command byte.  Commands are executed immediately after the
 * last byte has been received.
 *
 * Format of a command request:
 *   <number of bytes to follow> <command byte> <arg> <arg> ...
 * Examples:
 *   01 AB         Command AB, no args
 *   03 DE AA 55   Command DE, args: [AA, 55]
 *
 * Format of a command response:
 *   <number of bytes to follow> <ack|nak> <arg> <arg> ...
 * Examples:
 *   01 06         Command acknowledged, no args
 *   02 06 AA      Command acknowledged, args: [AA]
 *   01 15         Command not acknowledged, no args
 *   03 15 AA 55   Command not acknowledged, args: [AA, 55]
 */
void cmd_receive_byte(uint8_t c)
{
    // receive command length byte
    if (cmd_expected_length == 0)
    {
        if (c == 0) // invalid, command length must be 1 byte or longer
        {
            cmd_reply_nak();
            cmd_init();
        }
        else
        {
            cmd_expected_length = c;
            cmd_timer_start();
        }
    }
    // receive command byte(s)
    else
    {
        cmd_buf[cmd_buf_index++] = c;
        cmd_timer_start();

        if (cmd_buf_index == cmd_expected_length)
        {
            cmd_timer_stop();
            cmd_dispatch();
            cmd_init();
        }
    }
}

/*************************************************************************
 * Main
 *************************************************************************/

ISR(BADISR_vect)
{
    led_blink(LED_RED,1);
}

void receive_and_run_command()
{
    uint8_t c;
    if (buf_has_byte(&uart_rx_buffer))
    {
        c = buf_read_byte(&uart_rx_buffer);
        cmd_receive_byte(c);
    }
}

int main()
{
    led_init();
    uart_init();
    cmd_init();
    spi_slave_init();
    upd_init();
    sei();

    uart_puts("\nstart of program\n");

    while(1)
    {
        if (upd_cmds_buf_read_index != upd_cmds_buf_write_index)
        {
            upd_command_t updcmd;
            updcmd = upd_cmds_buf[upd_cmds_buf_read_index];
            upd_cmds_buf_read_index++;

            uint8_t i;
            for (i=0; i<updcmd.size; i++)
            {
                uart_puthex_byte(updcmd.data[i]);
                uart_putc(' ');
            }
            uart_putc('\n');


        }

    }
}