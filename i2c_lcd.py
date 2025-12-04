import time
from machine import I2C

# LCD Constants
LCD_I2C_ADDR = 0x27
LCD_WIDTH = 16
LCD_HEIGHT = 2
LCD_CHR = 1
LCD_CMD = 0
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
LCD_BACKLIGHT = 0x08
ENABLE = 0x04

class I2cLcd:
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.num_lines = num_lines
        self.num_columns = num_columns
        
        time.sleep_ms(20)
        self.lcd_byte(0x03, LCD_CMD)
        self.lcd_byte(0x03, LCD_CMD)
        self.lcd_byte(0x03, LCD_CMD)
        self.lcd_byte(0x02, LCD_CMD)

        self.lcd_byte(0x28, LCD_CMD)
        self.lcd_byte(0x0C, LCD_CMD)
        self.lcd_byte(0x06, LCD_CMD)
        self.lcd_byte(0x01, LCD_CMD)
        time.sleep_ms(5)

    def lcd_byte(self, bits, mode):
        bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
        bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

        self.i2c.writeto(self.i2c_addr, bytearray([bits_high | ENABLE]))
        time.sleep_us(50) # Enable pulse
        self.i2c.writeto(self.i2c_addr, bytearray([bits_high & ~ENABLE]))
        time.sleep_us(100)

        self.i2c.writeto(self.i2c_addr, bytearray([bits_low | ENABLE]))
        time.sleep_us(50)
        self.i2c.writeto(self.i2c_addr, bytearray([bits_low & ~ENABLE]))
        time.sleep_us(100)

    def clear(self):
        self.lcd_byte(0x01, LCD_CMD)
        time.sleep_ms(2)

    def move_to(self, col, row):
        if row == 0:
            addr = LCD_LINE_1 + col
        else:
            addr = LCD_LINE_2 + col
        self.lcd_byte(addr, LCD_CMD)

    def put_str(self, message):
        for char in message:
            self.lcd_byte(ord(char), LCD_CHR)
