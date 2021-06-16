import socket 
from _thread import start_new_thread
from time import sleep
    
# socket anlegen
host = '192.168.178.9'
port = 5555
sock = socket.socket()
try:
    sock.connect((host, port))
    username_is_invalid = 1
    while username_is_invalid:
        username = input("Input an username. (max. 16 characters)\n")
        sock.send(username.encode())
        username_is_invalid = int(sock.recv(1024).decode())
        if username_is_invalid:
            print("Username is already taken. Choose another name.")
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
sleep(1)

try:
    while True: #Sendeschleife
        msg = input("[YOU]: ")
        sock.send(msg.encode())
except ConnectionResetError:
        print("Server closed. Closing...")
        exit()
