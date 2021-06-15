import socket
from _thread import start_new_thread
from datetime import datetime

host = '127.0.0.1'
port = 5555
#socket anlegen
sock = socket.socket()
sock.bind((host, port))
sock.listen(1)
clients_list = []

print(f"Server({host}) listening on port {port}")
server_msg = f"New session started at {datetime.now().strftime('%d.%m.%Y - %H:%M:%S')}"
print(server_msg)
with open('history.txt', 'a') as text_file:
    text_file.write(server_msg + '\n')

def handle_client(conn, addr):
    print(f"{addr[0]} connected.")
    try:
        with open('history.txt', 'r') as text_file:
                conn.send(text_file.read().encode())
        conn.send("Welcome to the Server.".encode())
        # Client wird der Clientliste hinzugefuegt
        clients_list.append(conn)
        while True: # Empfangsschleife
            # Warten auf Nachrichten der Clientseite
            msg = conn.recv(1024)
            # Erfassen der Empfangszeit
            now = datetime.now().strftime("%H:%M")
            # Ausgabe der Clientnachricht in der Serverkonsole
            msg = f"[{addr[0]} - {now}]: {msg.decode()}"
            print(msg)
            # Weiterleiten der Nachricht an andere Clients
            broadcast(msg, conn)
            # Protokolierung des Chatverlaufs
            with open('history.txt', 'a') as text_file:
                text_file.write(msg + '\n')
    except ConnectionResetError:
        clients_list.remove(conn)
        print(f"{addr[0]} disconnected.")
        broadcast(f"{addr[0]} disconnected.")

def broadcast(msg, conn=None):
    if conn is None:
        for client in clients_list:
            try:
                client.send(msg.encode())
            except  ConnectionResetError:
                print(f"{addr[0]} disconnected.")
                clients_list.remove(conn)
    else:
        for client in clients_list:
            if client is not conn:
                try:
                    client.send(msg.encode())
                except  ConnectionResetError:
                    print(f"{addr[0]} disconnected.")
                    clients_list.remove(conn)

while True: #Serverschleife 
    # Auf neuen Client warten
    conn, addr = sock.accept()
    # Neuen Thread erstellen, der die Client Funktion aufruft.
    start_new_thread(handle_client, (conn, addr))