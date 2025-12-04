# Enigma Machine with ESP32 & Telegram

This project implements a distributed Enigma Machine using two ESP32 microcontrollers. One ESP32 acts as the **Sender (Alice)**, encrypting messages and sending them via ESP-NOW. The other acts as the **Receiver (Bob)**, which receives the encrypted message, decrypts it, and forwards the result to a Telegram Chat.

## 📂 Project Structure

- `enigma.py`: Core logic of the Enigma Machine (Rotors, Reflector, Encryption).
- `main_sender.py`: Main script for the Sender ESP32 (Alice). Handles input, encryption, and ESP-NOW transmission.
- `main_receiver.py`: Main script for the Receiver ESP32 (Bob). Handles ESP-NOW reception, decryption, and Telegram integration.
- `esp_now_utils.py`: Helper class for handling ESP-NOW communication.
- `telegram_bot.py`: Helper class for sending messages to Telegram via Wi-Fi.
- `i2c_lcd.py`: Driver for the I2C LCD Display (16x2).

## 🛠 Hardware Requirements

- 2x ESP32 Development Boards
- 2x I2C LCD Displays (16x2) (Optional, but recommended for visual feedback)
- Jumper Wires

### Wiring (LCD)
| LCD Pin | ESP32 Pin |
|---------|-----------|
| VCC     | VIN / 5V  |
| GND     | GND       |
| SDA     | GPIO 21   |
| SCL     | GPIO 22   |

## ⚙️ Configuration

### 1. Receiver (Bob) Setup
Open `main_receiver.py` and update the following configuration variables:

```python
# Telegram Config
WIFI_SSID = "Your_WiFi_SSID"
WIFI_PASS = "Your_WiFi_Password"
TELEGRAM_TOKEN = "Your_Telegram_Bot_Token"
TELEGRAM_CHAT_ID = "Your_Chat_ID"
```

### 2. Sender (Alice) Setup
You need the MAC address of the Receiver ESP32. You can find it by running `import network; print(network.WLAN(network.STA_IF).config('mac'))` on the Receiver.

Open `main_sender.py` and update:

```python
# TARGET MAC ADDRESS (BOB)
TARGET_MAC = "FF:FF:FF:FF:FF:FF" # Replace with Receiver's MAC Address
```

## 🚀 How to Use

### Step 1: Upload Files
1. **Sender ESP32**: Upload `enigma.py`, `i2c_lcd.py`, `esp_now_utils.py`, and `main_sender.py`.
2. **Receiver ESP32**: Upload `enigma.py`, `i2c_lcd.py`, `esp_now_utils.py`, `telegram_bot.py`, and `main_receiver.py`.

### Step 2: Run the System
1. **Start the Receiver (Bob)**:
   - Run `main_receiver.py`.
   - It will connect to Wi-Fi and display "Waiting Alice..." on the LCD.

2. **Start the Sender (Alice)**:
   - Run `main_sender.py`.
   - Follow the **Setup Wizard** in the Serial Monitor (or LCD) to configure the Enigma Machine:
     - **Number of Rotors**: Choose between 1 and 5.
     - **Rotor Types**: Select from I, II, III, IV, V.
     - **Initial Positions**: Set the starting position (A-Z) for each rotor.

### Step 3: Send a Message
1. On the **Sender**, type your message in the Serial Monitor.
2. The characters will be encrypted in real-time and shown on the LCD.
3. Press **ENTER** to confirm sending.
4. Press **1** to confirm sending to Bob.

### Step 4: Receive & Decrypt
1. The **Receiver** will get the encrypted packet via ESP-NOW.
2. It will display "Msg Received!" on the LCD.
3. In the Serial Monitor (or via button logic if implemented), confirm decryption (Press **1**).
4. The Receiver uses the *same* rotor settings (sent in the packet) to decrypt the message.
5. The decrypted message is sent to your **Telegram Bot**.

## 🧩 Enigma Implementation Details
- **Rotors**: Simulates 5 historical rotors (I-V) with adjustable ring settings (Notch).
- **Reflector**: Uses Reflector B.
- **Double Stepping**: Implements the authentic rotor stepping mechanism.

## ⚠️ Troubleshooting
- **ESP-NOW Failure**: Ensure both ESP32s are on the same Wi-Fi channel (Default: 6). You can change this in `esp_now_utils.py` or `main_sender.py`.
- **Telegram Error**: Ensure the Receiver has internet access and the Bot Token/Chat ID are correct.
- **LCD Not Working**: Check the I2C address in the code (`0x27` is default) and wiring.
