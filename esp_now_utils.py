import network
import espnow
import json

class EspNowLink:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        # ESP-NOW requires Wi-Fi to be active, but not necessarily connected
        
        self.e = espnow.ESPNow()
        self.e.active(True)

    def set_channel(self, channel):
        """Sets the Wi-Fi channel (1-13). Sender and Receiver MUST match."""
        try:
            self.wlan.config(channel=channel)
            return True
        except Exception as e:
            print(f"Error setting channel: {e}")
            return False
        
    def add_peer(self, mac_address_str):
        """Adds a peer by MAC address string (e.g. 'ff:ff:ff:ff:ff:ff')"""
        try:
            mac_bytes = bytes(int(x, 16) for x in mac_address_str.split(':'))
            self.e.add_peer(mac_bytes)
            return True
        except Exception as e:
            print(f"Error adding peer: {e}")
            return False

    def send_json(self, mac_address_str, data_dict):
        """Sends a dictionary as a JSON string to the target MAC"""
        try:
            mac_bytes = bytes(int(x, 16) for x in mac_address_str.split(':'))
            msg = json.dumps(data_dict)
            self.e.send(mac_bytes, msg)
            return True
        except Exception as e:
            print(f"Send Error: {e}")
            return False

    def receive_json(self):
        """Checks for incoming messages. Returns (mac, data_dict) or None."""
        host, msg = self.e.recv(0) # 0 timeout = non-blocking
        if msg:
            try:
                data_str = msg.decode()
                data = json.loads(data_str)
                # Convert host bytes to hex string
                host_str = ':'.join('{:02x}'.format(x) for x in host)
                return host_str, data
            except ValueError:
                print("Received non-JSON message")
                return None
        return None
