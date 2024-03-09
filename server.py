""" File Transfer Server

This script allows the users to create a server that listens
for incoming file transfers.
"""
import socket
import argparse

HEADERSIZE = 10

def main():
    try:
        listening_port = 5555

        help_max_conn = "an integer of the number of required connections"
        parser = argparse.ArgumentParser(
            description="Runs a server for file transfers"
            )
        parser.add_argument("max_connections", 
                            metavar="max_connections",
                            type=int,
                            nargs=1,
                            help=help_max_conn
                            )
        args = parser.parse_args()
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("", listening_port))

        connections = []

        server_socket.listen()
        print(f"Listening on port {listening_port}...")

        max_connections = args.max_connections[0]
        while len(connections) < max_connections:
            client_socket, _ = server_socket.accept()
            print("Connection has been accepted!")
            connections.append(client_socket)
        
        for conn in connections:
            data_processing(conn)

    except KeyboardInterrupt:
        print("The server has been closed...")
    finally:
        print("Closing server...")
        clean_up(server_socket, connections)


def data_processing(connection):
    buffer_size = 16

    headered = True
    buffer = ""
    data = ""
    file_name = "output"
    while True:
        data += connection.recv(buffer_size).decode()
        
        if headered:
            data_size = int(data[:HEADERSIZE])
            data = data[HEADERSIZE:]
            headered = False

        if data_size - len(buffer) < len(data):
            remaining_size = data_size - len(buffer)
            buffer += data[:remaining_size]
            data = data[remaining_size:]
        else:
            buffer += data
            data = ""

        # THIS IS ALWAYS BEING HIT WHEN YOU READ IN DATA
        # NOT WHEN YOU WRITE A FILE.
        if len(buffer) == data_size:
            if buffer == "exit": break

            with open(file_name, "a") as file:
                file.write(buffer)
            print(f"File has been written to {file_name}")

            headered = True
            buffer = ""

 



        # file_name = connection.recv(buffer_size).decode().strip()

        # if file_name == "exit": break
        # file_name += ".output"

        # while True:
        #     data = connection.recv(buffer_size).decode().strip()

        #     print(data)
        #     if data == "\x00": break


        # print(f"Output has been appended to {file_name}.")
            

def clean_up(server_socket, connections):
    for conn in connections:
        conn.close()
    server_socket.close()

if __name__ == "__main__":
    main() 