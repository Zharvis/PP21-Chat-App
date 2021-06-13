
import socket 
from datetime import datetime
from _thread import start_new_thread

# socket anlegen
host = '129.217.162.157'
port = 1200
contacts = dict()
contacts['Me'] = '129.217.162.157'
# define more contacts...
sock = socket.socket()
try:
    sock.connect((host, port))
except ConnectionRefusedError:
    print('Not able to connect to the Server, please make sure that the Server is running and try again later...')
    exit()


def start_client():
    start_new_thread(recieve_data, (host,port))
    while True:
        msg_client_input = input()
        time_client_input = str(datetime.now())[:16]
        sock.send(msg_client_input.encode())
        sock.send(time_client_input.encode())


def recieve_data(host,port):
    while True:
        try:
            start_msg = sock.recv(1024).decode()
            print(start_msg)
            history = sock.recv(1024).decode()
            print('History:')
            print(history.replace(contacts['Me'], 'Me'))
        except ConnectionResetError:
            print('Lost Connection to the Server...')
            break


start_client()
