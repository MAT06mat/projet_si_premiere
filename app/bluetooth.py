ADRESSE = "00:0E:EA:CF:58:14"

import socket, select
from time import time
from kivy.clock import Clock


class BlueToothObject:
    is_connect = False
    last_recieve = ""
    last_communication_time = 0
    time_out_duration = 2
    
    def __init__(self) -> None:
        self.socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) # Create socket
    
    async def connect(self):
        if not self.is_connect:
            port = 1  # Match the setting on the HC-05 module
            self.socket.connect((ADRESSE, port))
            self.is_connect = True
            BlueTooth.last_communication_time = time()
            self.send("connected")
            print("Bluetooth is connected.")
            return True
        return False
    
    def send(self, text):
        if self.is_connect:
            self.socket.send(bytes(text + '#', 'UTF-8'))
            return True
        return False
    
    def recieve(self):
        if self.is_connect:
            text = self.last_recieve
            while 1:
                ready_to_read, _, _ = select.select([self.socket], [], [], 0)
                if ready_to_read:
                    self.last_communication_time = time()
                    # Add the next caractere
                    char = repr(self.socket.recv(1)).split("'")[1]
                    if char == "#":
                        break
                    else:
                        text += char
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
            self.send("deconnected")
            self.socket.close()
            self.is_connect = False
            print("Bluetooth is deconnected.")
            return True
        return False


BlueTooth = BlueToothObject()


class Request:
    func = {"on_recieve": [], "bluetooth_time_out": []}
    speed = 0
    loop_iter = 0
    
    def __init__(self) -> None:
        # threading.Thread(target=self.loop).start()
        Clock.schedule_interval(self.loop, 1/20)
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
        if BlueTooth.is_connect:
            if time() - BlueTooth.last_communication_time > BlueTooth.time_out_duration:
                BlueTooth.deconnect()
                self.__call("bluetooth_time_out")
        
        if self.loop_iter >= 10:
            self.loop_iter = 0
            BlueTooth.send("p")

    def on_recieve(self, text):
        try:
            # text = "print-Bonjour"
            # text = "set-led-HIGH"
            text = text.split('-')
            if text[0] == "print":
                text.pop(0)
                text = "-".join(text)
                print("Print :", text)
            if text[0] == "speed":
                self.speed = int(text[1])
                print(self.speed)
        except Exception as e:
            print("Exeption on decode message :", e)
    

Api = Request()


__all__ = ("BlueTooth", "Api", )


if __name__ == '__main__':
    b = BlueToothObject()
    b.connect()
    while 1:
        text = input('>>> ')
        if text == "exit":
            break
        elif text != "":
            b.send(text)
        
        recept = None
        while 1:
            recept = b.recieve()
            if recept != "":
                print(recept)
            else:
                break
    
    b.deconnect()