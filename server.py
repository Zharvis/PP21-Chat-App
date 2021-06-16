import socket
from _thread import start_new_thread
from datetime import datetime

host = '192.168.178.9'
port = 5555
#socket anlegen
sock = socket.socket()
sock.bind((host, port))
sock.listen(1)
active_clients = dict()
print(f"Server({host}) listening on port {port}")
server_msg = f"New session started at {datetime.now().strftime('%d.%m.%Y - %H:%M:%S')}"
print(server_msg)
with open('history.txt', 'a') as text_file:
    text_file.write(server_msg + '\n')

def handle_client(conn, addr):
    try:
        username = ""
        username_is_invalid = 1
        while username_is_invalid:
            username = conn.recv(16).decode()
            if username not in active_clients:
                username_is_invalid = 0
                conn.send("0".encode())
            else:
                conn.send("1".encode())
            
        print(f"{username} connected.")
        with open('history.txt', 'r') as text_file:
                conn.send(text_file.read().encode())
        conn.send("Welcome to the Server.\n".encode())
        conn.send(f"Type '-p [address] [YOUR_MESSAGE]' to send private messages.".encode())
        # Client wird der Clientliste hinzugefuegt
        active_clients[username] = conn
        while True: # Empfangsschleife
            # Warten auf Nachrichten der Clientseite
            msg = conn.recv(1024)
            # Erfassen der Empfangszeit
            now = datetime.now().strftime("%H:%M")
            # Testen ob -private Modifier benutzt wurde
            if msg[:9] is "-private":
                pass
            # Ausgabe der Clientnachricht in der Serverkonsole
            msg = f"[{username} - {now}]: {msg.decode()}"
            print(msg)
            # Weiterleiten der Nachricht an andere Clients
            broadcast(msg, username)
            # Protokolierung des Chatverlaufs
            with open('history.txt', 'a') as text_file:
                text_file.write(msg + '\n')
    except ConnectionResetError:
        del active_clients[username]
        print(f"{username} disconnected.")
        broadcast(f"{username} disconnected.")

def broadcast(msg, username=None):
    if username is None:
        for clientname, conn in active_clients.items():
            try:
                conn.send(msg.encode())
            except  ConnectionResetError:
                print(f"{clientname} disconnected.")
                del active_clients[username]
    else:
        for clientname, conn in active_clients.items():
            if clientname is not username:
                try:
                    conn.send(msg.encode())
                except  ConnectionResetError:
                    print(f"{clientname} disconnected.")
                    del active_clients[username]

while True: #Serverschleife 
    # Auf neuen Client warten
    conn, addr = sock.accept()
    # Neuen Thread erstellen, der die Client Funktion aufruft.
    start_new_thread(handle_client, (conn, addr))