
import socket 
from datetime import datetime
from _thread import start_new_thread
import os


host = '129.217.162.157'
port = 1200

#directory festlegen
directory = os.path.dirname(__file__)

#socket anlegen
sock = socket.socket()
sock.bind((host, port))
sock.listen(1)

#client Liste erstellen
client_dict = dict()


def start_server():
    while True:
        conn, addr = sock.accept()
        print(addr[0], 'just joined the chat')
        conn.send(b"Welcome to the Server.\n")
        start_new_thread(handle_client, (conn,addr))
        try:
            with open(directory + '/history.txt','r') as text_file:
                history = text_file.read()
        except FileNotFoundError:
            print('The Start of something new...')
            open(directory + '/history.txt','a')
            with open(directory + '/history.txt','r') as text_file:
                history = text_file.read()
        conn.send(history.encode())


def handle_client(conn,addr):
    client_dict[str(addr[0])] = conn
    while True:
        #Warten auf Nachrichten der Clientseite
        msg_client_input = conn.recv(1024)
        time_client_input = conn.recv(1024)
        message = msg_client_input.decode()
        if message[0] == '@':
            reciever = message[1:16]
            msg_private = message[17:]
            time_msg_private = time_client_input
            send_private_message(reciever, addr, msg_private, time_msg_private)
            continue
        #Ausgabe der Clientnachricht
        print(time_client_input.decode()[:16], addr[0], msg_client_input.decode())
        #An andere Clients senden
        send_to_all_clients(msg_client_input, time_client_input, conn, addr)
        # Chatverlauf speichern
        with open(directory + '/history.txt','a') as text_file:
            text_file.write(time_client_input.decode() + ' ' + addr[0] + ' ' + msg_client_input.decode() + '\n')


def send_to_all_clients(msg_client_input, time_client_input, conn, addr):
    time_client_input += ' '.encode()
    for client in client_dict.values():
        if client == conn:
            continue
        client.send(time_client_input + addr[0].encode() + msg_client_input)

def send_private_message(reciever, addr, msg_private, time_msg_private):
    time_msg_private += ' '.encode()
    address = addr[0] + ' [private] '
    client_dict[reciever].send(time_msg_private + address.encode() + msg_private.encode())

    # syntax for private meesanges: '@[address of reciever] [private message]'

    
start_server()
