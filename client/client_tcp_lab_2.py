import socket
from enum import Enum
import struct
import threading
from threading import Thread
from typing import NoReturn
import os
import sys
import AdvTextDisplayer
from AdvTextDisplayer import PrintA, InputA
#import used modules



#some abstractions. these indicate the content of the messages.
class ClientSignalTypes:
    MESSAGE = bytes([0])
    JOIN = bytes([1])
    LEAVE = bytes([2])

class ServerSignalTypes:
    TEXT = bytes([0])
    CLOSE = bytes([1])
    ACCEPT = bytes([2])



# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)





#recieves messages. should run in parralel
def MessageReciever() -> NoReturn:
    try:
        while True:
            MsgBytes = sock.recv(5)
            MsgType = bytes([MsgBytes[0]])
            MsgLen = int.from_bytes(MsgBytes.lstrip(MsgType))
            if MsgType == ServerSignalTypes.CLOSE:
                raise BrokenPipeError("sigma")
            MsgBytes = sock.recv(MsgLen)
            PrintA(MsgBytes.decode())
    except:
        PrintA("Lost connection!")            
    
TextDisp = Thread(target= AdvTextDisplayer.init)
TextDisp.start()
PrintA("Input IP to connect to, 'localhost' to connect to yourself")
Address = InputA()
# connect to the server, listening on port 1313. server must run off of port 1313
server_address = (Address, 1313)
PrintA('Connecting to %s:%s' % server_address)
sock.connect(server_address)

PrintA("Input your username: ")
Name = bytes(InputA(),'utf-8')
sock.send(b''.join([ClientSignalTypes.JOIN, len(Name).to_bytes(4)]))
sock.send(Name)
if sock.recv(1) == ServerSignalTypes.CLOSE:
    PrintA("Server already had someone with this name or this name is invalid.")

#start messagereciever thread
MsgThread = Thread(target=MessageReciever, daemon=True)
MsgThread.start()

def Sender():
    while True: 
        # Prompt for input
        message_to_send = bytes(InputA(), 'utf-8')
        sock.send(b''.join([ClientSignalTypes.MESSAGE, len(message_to_send).to_bytes(4)]))
        #send input
        sock.sendall(bytes(message_to_send))

Senderthread = Thread(target=Sender,daemon=True)
Senderthread.start()
TextDisp.join()
#Close the server connection
sock.close()
