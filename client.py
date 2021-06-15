import socket 
from _thread import start_new_thread
    
# socket anlegen
host = '127.0.0.1'
port = 5555
sock = socket.socket()
try:
    sock.connect((host, port))
except ConnectionRefusedError:
    print("Cannot reach server. Closing...")
    exit()

def recv_msg():
    try:
        while True:
            msg = sock.recv(1024).decode()+'\n'
            print(msg)
    except ConnectionResetError:
        print("Server closed. Closing...")
        exit()

start_new_thread(recv_msg, ())

try:
    while True: #Sendeschleife
        msg = input("[YOU]: ")
        sock.send(msg.encode())
except ConnectionResetError:
        print("Server closed. Closing...")
        exit()
