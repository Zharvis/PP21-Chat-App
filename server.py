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
        # es wird auf einen neuen username gewartet
        username = ""
        username_is_invalid = 1
        while username_is_invalid:
            username = conn.recv(16).decode().lower()
            if username not in active_clients:
                username_is_invalid = 0
                conn.send("0".encode())
            else:
                conn.send("1".encode())
            
        print(f"{username} connected.")

        # dem neuen User wird der Chatverlauf gesendet
        with open('history.txt', 'r') as text_file:
                conn.send(text_file.read().encode())

        conn.send("Welcome to the Server.\n".encode())
        conn.send(f"Type '-p (USERNAME) (YOUR MESSAGE)' to send private messages.".encode())

        # Client wird der Clientliste hinzugefuegt
        active_clients[username] = conn

        # Empfangsschleife
        while True:

            # Warten auf Nachrichten der Clientseite
            msg = conn.recv(1024).decode()

            # Erfassen der Empfangszeit
            now = datetime.now().strftime("%H:%M")

            # Testen ob das Token -p für private Nachrichten benutzt wurde
            if msg[:2] == "-p":

                # Trennen der message in eine Liste
                msg_splitted = msg.split()

                # Ueberpruefen, ob es sich tatsaechlich einen aktiven User handelt
                if msg_splitted[1] in active_clients:

                    # Zusammenfuegen und Senden der zuvor getrennten Nachricht 
                    msg = f"[{username} - {now}] (private): {' '.join(msg_splitted[2:])}"
                    active_clients[msg_splitted[1]].send(msg.encode())

                    print(f"{username} sent a private message to {msg_splitted[1]}")
                else:
                    conn.send(f"Nobody named  {msg_splitted[1]}. Please check the name.".encode())
            else:
                msg = f"[{username} - {now}]: {msg}"

                # Ausgabe der Clientnachricht in der Serverkonsole
                print(msg)

                # Weiterleiten der Nachricht an andere Clients
                broadcast(msg, username)

                # Protokolierung des Chatverlaufs
                with open('history.txt', 'a') as text_file:
                    text_file.write(msg + '\n')

    # Fehler bei Verlust der Verbindung zum Client
    except ConnectionResetError:

        print(f"{username} disconnected.")

        # Loeschen des Clients aus der aktiven Nutzer Liste und Broadcast an die anderen User
        del active_clients[username]
        broadcast(f"{username} disconnected.")

def broadcast(msg, username=None):
    
    # Überprüfen, ob es sich um eine Nachricht vom Server handelt
    if username is None:
        for clientname, conn in active_clients.items():
            try:
                conn.send(msg.encode())

            # Fehler bei Verlust der Verbindung zum Client
            except  ConnectionResetError:

                print(f"{clientname} disconnected.")
                del active_clients[clientname]
                broadcast(f"{clientname} disconnected.")
    else:
        for clientname, conn in active_clients.items():

            # Ueberpruefen, ob es sich um den Sender selbst handelt
            if clientname is not username:

                try:
                    conn.send(msg.encode())
                
                # Fehler bei Verlust der Verbindung zum Client
                except  ConnectionResetError:

                    print(f"{clientname} disconnected.")

                    # Loeschen des Clients aus der aktiven Nutzer Liste und Broadcast an die anderen User
                    del active_clients[clientname]
                    broadcast(f"{clientname} disconnected.")
#Serverschleife 
while True:

    # Auf neuen Client warten
    conn, addr = sock.accept()
    
    # Neuen Thread erstellen, der die Client Funktion aufruft.
    start_new_thread(handle_client, (conn, addr))