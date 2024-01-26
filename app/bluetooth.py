ADRESSE = "00:0E:EA:CF:58:14"

import socket, select, threading
from time import sleep


class BlueToothObject:
    is_connect = False
    
    def __init__(self) -> None:
        self.socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) # Create socket
    
    async def connect(self):
        if not self.is_connect:
            port = 1  # Match the setting on the HC-05 module
            self.socket.connect((ADRESSE, port))
            self.is_connect = True
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
            text = ""
            while 1:
                ready_to_read, _, _ = select.select([self.socket], [], [], 0)
                if ready_to_read:
                    # Add the next caractere
                    char = repr(self.socket.recv(1)).split("'")[1]
                    if char == "#":
                        break
                    else:
                        text += char
                else:
                    break
            if len(text) >= 2:
                if text[-1] == "n" and text[-2] == "\\":
                    # Remove "\n" suffix 
                    text = text[:-2]
            return text
        else:
            return None
    
    def check_connection(self):
        if self.is_connect:
            # Utilisez getsockopt pour vérifier l'état de la connexion
            try:
                error_code = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                if error_code == 0:
                    return True  # La connexion est toujours active
                else:
                    print(f"Socket error: {error_code}")
                    return False  # Il y a une erreur sur le socket
            except socket.error as e:
                print(f"Error checking socket status: {e}")
                return False  # Il y a une erreur lors de la vérification du socket
        else:
            return False  # Le socket n'est pas connecté
    
    def deconnect(self):
        if self.is_connect:
            self.socket.close()
            self.is_connect = False
            print("Bluetooth is deconnected.")
            return True
        return False


BlueTooth = BlueToothObject()


class Request:
    func = {"on_recieve": []}
    continue_loop = True
    speed = 0
    
    def __init__(self) -> None:
        threading.Thread(target=self.loop).start()
        self.bind(self.recv)
    
    def bind(self, func, type="on_recieve"):
        self.func[type].append(func)
    
    def loop(self, *args):
        while self.continue_loop:
            # Reception d'un message
            recept = BlueTooth.recieve()
            if recept:
                for func in self.func["on_recieve"]:
                    func(recept)
            
            sleep(0.1)
    
    def command(self, *val):
        BlueTooth.send("-".join(val))
    
    def recv(self, text):
        try:
            # text = "print-Bonjour"
            # text = "set-led-HIGH"
            text = text.split('-')
            if text[0] == "print":
                text.pop(0)
                text = "-".join(text)
                print("Print :", text)
            if text[0] == "set":
                if text[1] == "speed":
                    self.speed = int(text[2])
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