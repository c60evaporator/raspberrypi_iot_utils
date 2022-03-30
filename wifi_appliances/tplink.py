import socket
from struct import pack
import json

#TPLink電球＆プラグ共通クラス
class TPLink_Common():
    def __init__(self, ip, port=9999):
        """Default constructor
        """
        self.__ip = ip
        self.__port = port
    
    def info(self):
        cmd = '{"system":{"get_sysinfo":{}}}'
        receive = self.send_command(cmd)
        return receive

    def info_dict(self):
        rjson = self.info()
        rdict = json.loads(rjson)
        return rdict
    
    def send_command(self, cmd, timeout=10):
        try:
            sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_tcp.settimeout(timeout)
            sock_tcp.connect((self.__ip, self.__port))
            sock_tcp.settimeout(None)
            sock_tcp.send(self.encrypt(cmd))
            data = sock_tcp.recv(2048)
            sock_tcp.close()

            decrypted = self.decrypt(data[4:])
            print("Sent:     ", cmd)
            print("Received: ", decrypted)
            return decrypted

        except socket.error:
            quit("Could not connect to host " + self.__ip + ":" + str(self.__port))
            return None

    def encrypt(self, string):
        key = 171
        result = pack('>I', len(string))
        for i in string:
            a = key ^ ord(i)
            key = a
            result += bytes([a])
        return result

    def decrypt(self, string):
        key = 171
        result = ""
        for i in string:
            a = key ^ i
            key = i
            result += chr(a)
        return result

#TPLinkプラグ操作用クラス
class TPLink_Plug(TPLink_Common):
    def on(self):
        cmd = '{"system":{"set_relay_state":{"state":1}}}'
        receive = self.send_command(cmd)

    def off(self):
        cmd = '{"system":{"set_relay_state":{"state":0}}}'
        receive = self.send_command(cmd)

    def ledon(self):
        cmd = '{"system":{"set_led_off":{"off":0}}}'
        receive = self.send_command(cmd)

    def ledoff(self):
        cmd = '{"system":{"set_led_off":{"off":1}}}'
        receive = self.send_command(cmd)
    
    def set_countdown_on(self, delay):
        cmd = '{"count_down":{"add_rule":{"enable":1,"delay":' + str(delay) +',"act":1,"name":"turn on"}}}'
        receive = self.send_command(cmd)

    def set_countdown_off(self, delay):
        cmd = '{"count_down":{"add_rule":{"enable":1,"delay":' + str(delay) +',"act":0,"name":"turn off"}}}'
        receive = self.send_command(cmd)
    
    def delete_countdown_table(self):
        cmd = '{"count_down":{"delete_all_rules":null}}'
        receive = self.send_command(cmd)

    def energy(self):
        cmd = '{"emeter":{"get_realtime":{}}}'
        receive = self.send_command(cmd)
        return receive

#TPLink電球操作用クラス
class TPLink_Bulb(TPLink_Common):
    def on(self):
        cmd = '{"smartlife.iot.smartbulb.lightingservice":{"transition_light_state":{"on_off":1}}}'
        receive = self.send_command(cmd)

    def off(self):
        cmd = '{"smartlife.iot.smartbulb.lightingservice":{"transition_light_state":{"on_off":0}}}'
        receive = self.send_command(cmd)

    def transition_light_state(self, hue: int = None, saturation: int = None, brightness: int = None,
                               color_temp: int = None, on_off: bool = None, transition_period: int = None,
                               mode: str = None, ignore_default: bool = None):
        # copy all given argument name-value pairs as a dict
        d = {k: v for k, v in locals().items() if k is not 'self' and v is not None}
        r = {
            'smartlife.iot.smartbulb.lightingservice': {
                'transition_light_state': d
            }
        }
        cmd = json.dumps(r)
        receive = self.send_command(cmd)
        print(receive)

    def brightness(self, brightness):
        self.transition_light_state(brightness=brightness)

    def purple(self, brightness = None, transition_period = None):
        self.transition_light_state(hue=277, saturation=86, color_temp=0, brightness=brightness, transition_period=transition_period)

    def blue(self, brightness = None, transition_period = None):
        self.transition_light_state(hue=240, saturation=100, color_temp=0, brightness=brightness, transition_period=transition_period)

    def cyan(self, brightness = None, transition_period = None):
        self.transition_light_state(hue=180, saturation=100, color_temp=0, brightness=brightness, transition_period=transition_period)

    def green(self, brightness = None, transition_period = None):
        self.transition_light_state(hue=120, saturation=100, color_temp=0, brightness=brightness, transition_period=transition_period)
    
    def yellow(self, brightness = None, transition_period = None):
        self.transition_light_state(hue=60, saturation=100, color_temp=0, brightness=brightness, transition_period=transition_period)

    def orange(self, brightness = None, transition_period = None):
        self.transition_light_state(hue=39, saturation=100, color_temp=0, brightness=brightness, transition_period=transition_period)
    
    def red(self, brightness = None, transition_period = None):
        self.transition_light_state(hue=0, saturation=100, color_temp=0, brightness=brightness, transition_period=transition_period)
    
    def lamp_color(self, brightness = None):
        self.transition_light_state(color_temp=2700, brightness=brightness)