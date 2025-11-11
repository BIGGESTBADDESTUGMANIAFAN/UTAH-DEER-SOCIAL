import socket
from time import sleep, time
from threading import Thread, current_thread
import re
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
# Bind the socket to the port localhost 1313
server_address = ('', 1313)
sock.bind(server_address)

#rude words! defalt word included in blacklist
Rudewords : set[str] = set(["fuck", "nigger", "bitch", "cunt", "ugmania", "porn", "java", "shit", "skibidi", '\0', '\t', '\n', '\r'])

Banned : set[str] = set()

def ChineseCensorship(OrigText:str) -> str:
    global Rudewords
    Newtext = OrigText
    for word in Rudewords:
        InsensitiveRudeword = re.compile(re.escape(word), re.IGNORECASE)
        Newtext = InsensitiveRudeword.sub('*'*len(word), Newtext)
    return Newtext

#sends a text message to all clients
def Sendall(Message:str)->None:
    MessageLen = len(Message)
    print(Message)
    for _, sock in Clients.copy().items():
        try:
            sock.send(b''.join([ServerSignalTypes.TEXT, MessageLen.to_bytes(4)]))
            sock.send(bytes(ChineseCensorship(Message), 'utf-8'))
        except:
            pass

def Send(Message:str, To:list[str]) -> None:    
    MessageLen = len(Message)
    print(f"To {(', ').join(To)}:", Message)
    for name in To:
        try:
            Clients[name].send(b''.join([ServerSignalTypes.TEXT, MessageLen.to_bytes(4)]))
            Clients[name].send(bytes(ChineseCensorship(Message), 'utf-8'))
        except:
            continue

#dictionary containing every online client.
Clients : dict[str, socket.socket] = {}

def Client_Loop(client : socket.socket, IP: str):
    global Clients
    Username = ''
    try:
        MsgBytes = client.recv(5)
        MsgType = bytes([MsgBytes[0]])
        MsgLen = int.from_bytes(MsgBytes.lstrip(MsgType))

        #save their username to the thread
        Username = client.recv(MsgLen).decode()
        current_thread().name = Username
        if Clients.get(Username) or Username.find(' ') != -1:
            raise NameError("Name exists")
        client.sendall(ServerSignalTypes.ACCEPT)
        Clients[Username] = client
        LastMsg = 0
        SuccessMsgs = 0
        while True:
            LastMsg = time()
            MsgBytes = client.recv(5)
            MsgType = bytes([MsgBytes[0]])
            MsgLen = int.from_bytes(MsgBytes.lstrip(MsgType))

            if MsgType == ClientSignalTypes.LEAVE:
                raise BrokenPipeError("broken pipe")
            MsgBytes = client.recv(MsgLen)
            if MsgType == ClientSignalTypes.MESSAGE and len(MsgBytes) > 0:
                Sendall('<' + Username + '>: ' + MsgBytes.decode())
            if LastMsg - time() < 1:
                SuccessMsgs += 1
                if SuccessMsgs > 15:
                    Send("Auto-kicked for spamming!", [Username])
                    raise BrokenPipeError("Too much spam!")
            else:
                SuccessMsgs = 0
    except NameError:
        client.sendall(ServerSignalTypes.CLOSE)
    except:
        if Username:
            if Clients.get(Username):
                Clients.pop(Username)
            Sendall(f"{Username} Left the chat!")
    finally:
        client.close()

def CommandThread():
    while True:
        try:
            inp = input()
            Args = inp.split(" ")
            cmd = Args.pop(0)
            match cmd.lower():
                case "list":
                    print(Clients)
                case "broadcast":
                    Sendall("<Server>: "+ " ".join(Args))
                case "kick":
                    Clients[' '.join(Args)].sendall(b''.join([ServerSignalTypes.CLOSE, int(0).to_bytes(4)]))
                    Clients[' '.join(Args)].close()
                case "blacklist":
                    Rudewords.add(Args[0])
                case "whitelist":
                    try:
                        Rudewords.remove(Args[0])
                    except:
                        print("word not in blacklist")
                case "help":
                    print("""list: lists all online clients 
broadcast <message>: broadcasts a message to all clients
kick <username>: kicks the specified user
ban <ip>: prevents the specified IP from connecting for the current session
unban <ip>: allows specified IP the ability to reconnect
banlist: prints the list of banned IPs
message <user> <message>: send a private message to a user
blacklist <word>: add the specified word to the blacklist
whitelist <word>: removes the specified word to the blacklist
help: display this message""")
                case "message":
                    Send("<Server>: " +' '.join(Args[1:]), [Args[0]])
                case "ban":
                    Banned.add(Args[0])
                case "unban":
                    try: Banned.remove(Args[0])
                    except: pass
                case "banlist":
                    print(Banned)
                case _:
                    print("unkown command " + cmd +"\nType 'help' to list all commands")
        except:
            print("Something went wrong, check you entered all arguments properly.")
            
        

Thread(target=CommandThread, daemon=True).start()

RecentConnections : dict[socket:(int,float)] = {}
#infinite loop. this handles new requests
while True:
    #listen for, and establish a connection with a user
    sock.listen(1)
    client, client_port = sock.accept()
    if client_port[0] in Banned:
        client.close()
    else:
        LastJoinTime = RecentConnections[client_port[0]][1] if RecentConnections.get(client_port[0]) else 0

        if RecentConnections.get(client_port[0]) and time()-RecentConnections[client_port[0]][1] < 60:
            RecentConnections[client_port[0]] = (RecentConnections[client_port[0]][0]+1, time())
        else:
            RecentConnections[client_port[0]] = (1, time())
        print(time()-LastJoinTime)
        if time()-LastJoinTime < 1:
            print(f"Auto-banned {client_port[0]}: Spam joining (suspected DOS attack < 1s between two joins)")
            Banned.add(client_port[0])
            client.close()
        elif RecentConnections[client_port[0]][0] > 10:
            print(f"Auto-banned {client_port[0]}: Spam joining (suspected DOS attack < 60s between 10 consecutive joins)")
            RecentConnections.pop(client_port[0])
            Banned.add(client_port[0])
            client.close()
        else:
            print('Connection from client %s:%s' % client_port )
            #start a thread for the user
            Thread(target=Client_Loop, kwargs={"client":client, 'IP': client_port[0]}, daemon=True).start()