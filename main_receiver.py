import sys
import uselect
import time
from machine import Pin, I2C
from enigma import MaquinaEnigma
from i2c_lcd import I2cLcd
from esp_now_utils import EspNowLink
from telegram_bot import TelegramBot

# --- CONFIGURATION ---
# LCD Pins (I2C)
I2C_SDA = 21
I2C_SCL = 22
I2C_ADDR = 0x27

# Telegram Config
WIFI_SSID = "WiFiSSID"
WIFI_PASS = "WiFiPass"
TELEGRAM_TOKEN = "TelegramToken"
TELEGRAM_CHAT_ID = "TelegramChatID"

# --- INPUT HANDLING ---
spoll = uselect.poll()
spoll.register(sys.stdin, uselect.POLLIN)

def read_char():
    if spoll.poll(0):
        return sys.stdin.read(1)
    return None

def wait_for_input(lcd, prompt_line1, prompt_line2, valid_options=None):
    print(f"\n{prompt_line1}")
    print(f"{prompt_line2}")
    
    if lcd:
        lcd.clear()
        lcd.put_str(prompt_line1[:16])
        lcd.move_to(0, 1)
        lcd.put_str(prompt_line2[:16])
        
    while True:
        char = read_char()
        if char:
            char = char.upper()
            if valid_options:
                if char in valid_options:
                    return char
            else:
                return char
        time.sleep(0.05)

# --- INITIALIZATION ---

def setup():
    print("Initializing Enigma Receiver (Bob)...")
    
    # 1. Setup LCD
    try:
        i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=400000)
        devices = i2c.scan()
        if devices:
            addr = devices[0]
        else:
            addr = I2C_ADDR
        lcd = I2cLcd(i2c, addr, 2, 16)
        lcd.clear()
        lcd.put_str("Enigma Receiver")
        time.sleep(2)
    except Exception as e:
        print(f"LCD Init Error: {e}")
        lcd = None

    # 2. Setup ESP-NOW
    link = EspNowLink()
    
    # 3. Setup Telegram
    bot = TelegramBot(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, WIFI_SSID, WIFI_PASS)
    # Connect on startup so we are ready
    if lcd:
        lcd.clear()
        lcd.put_str("Connecting WiFi...")
    bot.connect_wifi()
    
    if lcd:
        lcd.clear()
        lcd.put_str("Waiting Alice...")
        
    return lcd, link, bot

# --- MAIN LOOP ---

def main():
    lcd, link, bot = setup()
    
    print("\n--- BOB (RECEIVER) READY ---")
    print("Waiting for messages from Alice...")
    
    while True:
        # Check for incoming ESP-NOW packet
        packet = link.receive_json()
        
        if packet:
            sender_mac, data = packet
            print(f"\nReceived from {sender_mac}: {data}")
            
            encrypted_text = data.get('text', '')
            rotors = data.get('rotors', [])
            positions = data.get('pos', '')
            
            # Display: "Message '{msg}' received"
            print(f"Message '{encrypted_text}' received.")
            if lcd:
                lcd.clear()
                lcd.put_str("Msg Received!")
                lcd.move_to(0, 1)
                lcd.put_str(encrypted_text[:16])
                time.sleep(2)
            
            # Prompt: "1: Decrypt"
            choice = wait_for_input(lcd, "1: Decrypt", "2: Ignore", ['1', '2'])
            
            if choice == '1':
                # Decrypt
                print("Decrypting...")
                if lcd:
                    lcd.clear()
                    lcd.put_str("Decrypting...")
                
                # Init Enigma with received settings
                enigma = MaquinaEnigma(rotors, positions)
                decrypted_text = enigma.cifrar_mensaje(encrypted_text)
                
                print(f"Decrypted: {decrypted_text}")
                
                # Display "Sending message..."
                if lcd:
                    lcd.clear()
                    lcd.put_str("Sending Tgram...")
                
                # Send to Telegram
                msg_text = (
                    f"🔐 *ENIGMA DECRYPTED*\n\n"
                    f"⚙️ *Rotors:* `{'-'.join(rotors)}`\n"
                    f"📍 *Positions:* `{positions}`\n\n"
                    f"🔒 *Encrypted:* `{encrypted_text}`\n"
                    f"🔓 *Decrypted:* `{decrypted_text}`"
                )
                
                if not bot.wlan.isconnected():
                    bot.connect_wifi()
                    
                success = bot.send_message(msg_text)
                
                if lcd:
                    lcd.move_to(0, 1)
                    lcd.put_str("Sent!" if success else "Error!")
                    time.sleep(2)
                    lcd.clear()
                    lcd.put_str("Waiting Alice...")
            else:
                if lcd:
                    lcd.clear()
                    lcd.put_str("Ignored.")
                    time.sleep(1)
                    lcd.clear()
                    lcd.put_str("Waiting Alice...")

        time.sleep(0.1)

if __name__ == "__main__":
    main()
