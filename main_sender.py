import sys
import uselect
import time
from machine import Pin, I2C
from enigma import MaquinaEnigma
from i2c_lcd import I2cLcd
from esp_now_utils import EspNowLink

# --- CONFIGURATION ---
# LCD Pins (I2C)
I2C_SDA = 21
I2C_SCL = 22
I2C_ADDR = 0x27

# TARGET MAC ADDRESS (BOB)
# REPLACE THIS with the MAC address from get_mac.py running on the other ESP32
TARGET_MAC = "FF:FF:FF:FF:FF:FF" 

# --- INPUT HANDLING ---

spoll = uselect.poll()
spoll.register(sys.stdin, uselect.POLLIN)

def read_char():
    """Reads a single character from Serial Monitor (non-blocking)"""
    if spoll.poll(0):
        return sys.stdin.read(1)
    return None

def wait_for_input(lcd, prompt_line1, prompt_line2, valid_options=None):
    """Waits for valid input from Serial Monitor"""
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
                if 'A' <= char <= 'Z':
                    return char
        time.sleep(0.05)

# --- SETUP WIZARD ---

def run_setup_wizard(lcd):
    """Runs the interactive setup on LCD/Serial"""
    
    # 1. How many rotors?
    num_rotors = int(wait_for_input(lcd, "How many rotors?", "1-5", ['1', '2', '3', '4', '5']))
    print(f"Selected: {num_rotors}")
    
    selected_rotors = []
    available_rotors = ['I', 'II', 'III', 'IV', 'V']
    
    # 2. Which rotors?
    for i in range(num_rotors):
        options_str = ",".join(available_rotors)
        rotor_map = {'1':'I', '2':'II', '3':'III', '4':'IV', '5':'V'}
        
        while True:
            choice = wait_for_input(lcd, f"Rotor {i+1}?", options_str, ['1', '2', '3', '4', '5'])
            rotor_name = rotor_map[choice]
            
            if rotor_name in available_rotors:
                selected_rotors.append(rotor_name)
                available_rotors.remove(rotor_name)
                print(f"Selected: {rotor_name}")
                break
            else:
                print("Already selected!")
                if lcd:
                    lcd.clear()
                    lcd.put_str("Used! Pick other")
                    time.sleep(1)

    # 3. Positions
    positions = []
    for i in range(num_rotors):
        rotor_name = selected_rotors[i]
        pos = wait_for_input(lcd, f"Pos Rotor {rotor_name}?", "A-Z")
        positions.append(pos)
        print(f"Position: {pos}")

    return selected_rotors, "".join(positions)

# --- INITIALIZATION ---

def setup():
    print("Initializing Enigma Sender (Alice)...")
    
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
        lcd.put_str("Enigma Sender")
        time.sleep(2)
    except Exception as e:
        print(f"LCD Init Error: {e}")
        lcd = None

    # 2. Run Wizard
    rotors, positions = run_setup_wizard(lcd)
    
    # 3. Setup Enigma
    enigma = MaquinaEnigma(rotors, positions)
    
    # 4. Setup ESP-NOW
    link = EspNowLink()
    link.set_channel(6)
    if TARGET_MAC == "FF:FF:FF:FF:FF:FF":
        print("WARNING: Using Broadcast MAC. Please set TARGET_MAC in code.")
    
    link.add_peer(TARGET_MAC)
    
    return lcd, enigma, link, rotors, positions

# --- MAIN LOOP ---

def main():
    lcd, enigma, link, rotors, positions = setup()
    
    buffer_raw = ""
    buffer_encrypted = ""
    
    if lcd:
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.put_str("Ready to type...")
    
    print("\n--- ALICE (SENDER) READY ---")
    print("Type characters to encrypt.")
    print("Press ENTER to send to Bob.")
    print("Press TAB to clear.")
    
    while True:
        char = read_char()
        
        if char:
            # Handle special characters
            if char == '\n' or char == '\r':
                # Confirmation Step
                if buffer_encrypted:
                    print(f"\n\nMessage to send: {buffer_encrypted}")
                    print("Confirm send? (1=Yes, 2=No)")
                    
                    if lcd:
                        lcd.clear()
                        lcd.put_str(f"Send \"{buffer_raw[:10]}\"?")
                        lcd.move_to(0, 1)
                        lcd.put_str("1:Yes 2:No")
                    
                    while True:
                        confirm = read_char()
                        if confirm == '1':
                            # YES - Send via ESP-NOW
                            print("Sending to Bob...")
                            if lcd:
                                lcd.clear()
                                lcd.put_str("Sending...")
                            
                            # Prepare Packet
                            packet = {
                                "rotors": rotors,
                                "pos": positions,
                                "text": buffer_encrypted,
                                "raw": buffer_raw # Optional: Send raw too if Bob needs to verify? 
                                                  # But Bob is supposed to decrypt. 
                                                  # Let's send just what's needed for decryption.
                            }
                            
                            success = link.send_json(TARGET_MAC, packet)
                            
                            if lcd:
                                lcd.move_to(0, 1)
                                lcd.put_str("Sent!" if success else "Failed!")
                                time.sleep(1)
                                lcd.clear()
                                lcd.put_str("Ready...")
                            
                            buffer_raw = ""
                            buffer_encrypted = ""
                            break
                            
                        elif confirm == '2':
                            # NO - Cancel
                            print("Cancelled.")
                            if lcd:
                                lcd.clear()
                                lcd.put_str("Cancelled")
                                time.sleep(1)
                                lcd.clear()
                                lcd.put_str(buffer_raw[-16:])
                                lcd.move_to(0, 1)
                                lcd.put_str(buffer_encrypted[-16:])
                            break
                        time.sleep(0.1)
                continue
                
            if char == '\t': # Tab to clear
                buffer_raw = ""
                buffer_encrypted = ""
                enigma.reset()
                if lcd:
                    lcd.clear()
                    lcd.put_str("Cleared")
                    time.sleep(0.5)
                    lcd.clear()
                print("\nCleared.")
                continue

            # Process printable characters
            if ' ' <= char <= '~':
                encrypted_char = enigma.cifrar_letra(char)
                buffer_raw += char
                buffer_encrypted += encrypted_char
                
                print(f"{char} -> {encrypted_char}")
                
                if lcd:
                    if len(buffer_raw) == 1:
                        lcd.clear()
                    
                    display_raw = buffer_raw[-16:]
                    display_enc = buffer_encrypted[-16:]
                    
                    lcd.move_to(0, 0)
                    lcd.put_str(display_raw)
                    lcd.move_to(0, 1)
                    lcd.put_str(display_enc)

if __name__ == "__main__":
    main()
