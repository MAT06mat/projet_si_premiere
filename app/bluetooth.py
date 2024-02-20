ADRESSE = "00:0E:EA:CF:58:14"


from time import time, sleep
from kivy.clock import Clock
from kivy.app import App

import sys


if sys.platform == "win32":
    import socket , select
else:
    from jnius import autoclass

    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
    BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
    InputStreamReader = autoclass('java.io.InputStreamReader')
    BufferedReader = autoclass('java.io.BufferedReader')
    UUID = autoclass('java.util.UUID')
    
    def get_socket_stream():
        paired_devices = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
        socket = None
        for device in paired_devices:
            if device.getAddress() == ADRESSE:
                socket = device.createRfcommSocketToServiceRecord(
                    UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
                send_stream = socket.getOutputStream()
                reader = InputStreamReader(socket.getInputStream(), 'US-ASCII')
                recv_stream = BufferedReader(reader)
                break
        return socket, recv_stream, send_stream


class BlueToothObject:
    is_connect = False
    last_recieve = ""
    last_communication_time = 0
    time_out_duration = 3
    connexion_time = 0
    last_send = time()
    min_time_to_send = 0.2
    next_text_to_send = ""
    recv_stream = None
    send_stream = None
    
    def __init__(self) -> None:
        self.socket = None
    
    async def connect(self):
        if not self.socket:
            if sys.platform == "win32":
                self.socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) # Create socket 
            else:
                self.socket, self.recv_stream, self.send_stream = get_socket_stream()
        
        if not self.is_connect:
            if sys.platform == "win32":
                port = 1  # Match the setting on the HC-05 module
                self.socket.connect((ADRESSE, port))
            else:
                self.socket.connect()
            self.send("co")
            print("Bluetooth is connected.")
            self.is_connect = True
            self.last_communication_time = time()
            self.connexion_time = time()
            return True
        return False
    
    def send(self, text):
        if self.is_connect and (self.send_stream or sys.platform == "win32"):
            self.next_text_to_send += text + "#"
            return True
        return False

    def update(self):
        try:
            if self.is_connect and (self.send_stream or sys.platform == "win32"):
                if self.next_text_to_send != "":
                    if time() - self.last_send > self.min_time_to_send:
                        if sys.platform == "win32":
                            self.socket.send(bytes(self.next_text_to_send, 'UTF-8'))
                        else:
                            self.send_stream.write(bytes(self.next_text_to_send, 'UTF-8'))
                            self.send_stream.flush()
                        self.next_text_to_send = ""
                        self.last_send = time()
        except:
            pass
    
    def recieve(self):
        if self.is_connect:
            text = self.last_recieve
            while 1:
                if sys.platform == "win32":
                    ready_to_read, _, _ = select.select([self.socket], [], [], 0)
                    if ready_to_read:
                        self.last_communication_time = time()
                        # Add the next caractere
                        try:
                            char_byte = self.socket.recv(1)
                            char_str = char_byte.decode(encoding="ASCII")
                            if char_str == "#":
                                break
                            else:
                                text += char_str
                        except Exception as e:
                            print("Exeption lors du decodage :", e)
                    else:
                        self.last_recieve = text
                        return None
                else:
                    ready_to_read = self.recv_stream.ready()
                    if ready_to_read > 0:
                        self.last_communication_time = time()
                        # Add the next caractere
                        try:
                            char_int = self.recv_stream.read()
                            char_bytes = char_int.to_bytes(1, byteorder="little")
                            char_str = char_bytes.decode(encoding="ASCII")
                            if char_str == "#":
                                break
                            else:
                                text += char_str
                        except:
                            pass
                    else:
                        self.last_recieve = text
                        return None
            if len(text) >= 2:
                if text[-1] == "n" and text[-2] == "\\":
                    # Remove "\n" suffix 
                    text = text[:-2]
            self.last_recieve = ""
            return text
        else:
            return None
    
    def deconnect(self):
        if self.is_connect:
            self.send("de")
            self.socket.close()
            self.socket = None
            self.is_connect = False
            print("Bluetooth is deconnected.")
            return True
        return False


BlueTooth = BlueToothObject()


class Request:
    func = {"on_recieve": []}
    dist = 0
    brightness = 0
    loop_iter = 0
    
    def __init__(self) -> None:
        Clock.schedule_interval(self.loop, 1/60)
        self.bind(self.on_recieve)
    
    def bind(self, func, type="on_recieve"):
        self.func[type].append(func)
    
    def __call(self, type, *args):
        for func in self.func[type]:
            func(*args)
    
    def loop(self, *args):
        self.loop_iter += 1
        
        # Déctection de la reception d'un message
        recept = BlueTooth.recieve()
        if recept:
            self.__call("on_recieve", recept)
        
        # Déctection de la déconnection
        if BlueTooth.is_connect and BlueTooth.connexion_time + 5 < time():
            if time() - BlueTooth.last_communication_time > BlueTooth.time_out_duration:
                self.deconnect("Appareil déconnecté (Time Out)")
        
        if self.loop_iter >= 60:
            self.loop_iter = 0
            BlueTooth.send("p")
        
        BlueTooth.update()
    
    def deconnect(self, message=""):
        BlueTooth.deconnect()
        app = App.get_running_app()
        if message != "":
            for screen in app.manager.screens:
                if screen.name == "Connection":
                    screen.children[0].connect_message.message(message)
        app.manager.pop_all()
        self.dist = 0
        self.brightness = 0

    def on_recieve(self, text):
        try:
            # text = "print:Bonjour"
            # text = "set:led:HIGH"
            text = text.split(':')
            if text[0] == "p":
                text.pop(0)
                text = ":".join(text)
                print("Print :", text)
            if text[0] == "b":
                try:
                    self.brightness = int(text[1])
                except:
                    self.brightness = 0
                print("Brightness:", self.brightness)
            if text[0] == "d":
                try:
                    self.dist = int(text[1])
                except:
                    self.dist = 0
                print("dist:", self.dist)
        except Exception as e:
            print("Exeption on decode message :", e)
    

Api = Request()


__all__ = ("BlueTooth", "Api", )