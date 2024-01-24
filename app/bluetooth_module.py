ADRESSE = "00:0E:EA:CF:58:14"

UUID_List = "00001101-0000-1000-8000-00805f9b34fb"
import socket

port = 1  # Match the setting on the HC-05 module
s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
s.connect((ADRESSE, port))
print("Connected. Type something...")
while 1:
    text = input("Send : ")
    if text == "quit":
        break
    s.send(bytes(text + '#', 'UTF-8'))
s.close()