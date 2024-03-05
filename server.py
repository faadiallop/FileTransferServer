""" File Transfer Client

This script allows the users to create a server that listens
for incoming file transfers.
"""
import socket
import argparse

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

        max_connections = args.max_connections[0]
        while len(connections) < max_connections:
            client_socket, _ = server_socket.accept()
            print("Connection has been accepted!")
            connections.append(client_socket)
        
        for conn in connections:
            data_processing(conn)

        print("Output has been appended to output.txt.")
    except KeyboardInterrupt:
        print("The server has been closed...")
    finally:
        print("Closing server...")
        clean_up(server_socket, connections)

def data_processing(connection):
    buffer_size = 1024

    while True:
        data = connection.recv(buffer_size).decode()

        if not data: break
        with open("output.txt", "a") as file:
            file.write(data)
            

def clean_up(server_socket, connections):
    for conn in connections:
        conn.close()
    server_socket.close()

if __name__ == "__main__":
    main() 