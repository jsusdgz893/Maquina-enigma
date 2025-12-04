import network
import urequests
import time

class TelegramBot:
    def __init__(self, token, chat_id, ssid=None, password=None):
        self.token = token
        self.chat_id = chat_id
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)

    def connect_wifi(self):
        """Connects to Wi-Fi if credentials are provided"""
        if not self.ssid:
            print("No Wi-Fi credentials provided.")
            return False
            
        self.wlan.active(True)
        if not self.wlan.isconnected():
            print('Connecting to network...')
            self.wlan.connect(self.ssid, self.password)
            
            # Wait for connection with timeout
            max_wait = 10
            while max_wait > 0:
                if self.wlan.status() < 0 or self.wlan.status() >= 3:
                    break
                max_wait -= 1
                print('waiting for connection...')
                time.sleep(1)
                
        if self.wlan.isconnected():
            print('Network config:', self.wlan.ifconfig())
            return True
        else:
            print('Connection failed')
            return False

    def send_message(self, message):
        """Sends a message to the configured Telegram chat"""
        if not self.wlan.isconnected():
            print("Wi-Fi not connected. Cannot send Telegram message.")
            return False
            
        url = "https://api.telegram.org/bot{}/sendMessage".format(self.token)
        data = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        try:
            headers = {'Content-Type': 'application/json'}
            response = urequests.post(url, json=data, headers=headers)
            response.close()
            return True
        except Exception as e:
            print("Error sending Telegram message:", e)
            return False
