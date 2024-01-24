ADRESSE = "00:0E:EA:CF:58:14"

import socket, select


class BlueTooth:
    def __init__(self) -> None:
        self.socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) # Create socket
    
    def connect(self):
        port = 1  # Match the setting on the HC-05 module
        self.socket.connect((ADRESSE, port))
        print("Bluetooth is connected.")
    
    def send(self, text):
        self.socket.send(bytes(text + '#', 'UTF-8'))
    
    def recieve(self):
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
    
    def deconnect(self):
        self.socket.close()
        print("Bluetooth is deconnected.")


if __name__ == '__main__':
    b = BlueTooth()
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