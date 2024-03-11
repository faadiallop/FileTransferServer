""" File Transfer Server

This script allows the user to create a server that listens
for incoming file transfers.
If formatted corrected this server can also be interacted with through
programs such as netcat.
This program is an implementation of the File Transfer Protocol.
"""
import socket
import argparse

HEADERSIZE = 10

def main():
    """ Parameters: None
        Return: None

        This function runs a TCP server socket to send files to.
        The server copies those files to the current directory.
        The file input from those clients is handled by other functions.
    """
    try:
        listening_port = 5555

        args = process_arguments()
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

def process_arguments():
    """ Parameters: None
        Return: argparse.Namespace object with the arguments.
        This function reads in the command line arguments and outputs
        a argparse.Namespace object.
    """
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
    return parser.parse_args()

def data_processing(connection):
    """ Parameters: connection: A client socket.
        Return: None

        This function processes the file bytes from the client to copy
        that file to a file called {file name}.output.
    """
    buffer_size = 16

    headered = True
    buffer = ""
    data = ""
    file_name = ""
    while True:
        data += connection.recv(buffer_size).decode()

        if headered:
            header = data[:HEADERSIZE]
            # Last number identifies if this is a new file
            data_size, new_file = int(header[:-1]), bool(int(header[-1]))
            data = data[HEADERSIZE:]
            headered = False

        if data_size - len(buffer) < len(data):
            remaining_size = data_size - len(buffer)
            buffer += data[:remaining_size]
            data = data[remaining_size:]
        else:
            buffer += data
            data = ""

        if len(buffer) == data_size:
            if buffer == "exit":
                break

            if buffer == "done":
                print(f"File has been written to {file_name}")
            elif new_file:
                file_name = buffer + ".output"
                new_file = False
            else:
                # YOU'RE OPENING THE FILE 4 TIMES FOR INPUT WHEN
                # YOU'RE ONLY SUPPOSED TO OPEN IT TWICE:w
                with open(file_name, "a", encoding="utf-8") as file:
                    file.write(buffer)

            headered = True
            buffer = ""

def clean_up(server_socket, connections):
    """ Parameters: server_socket: The socket for the server.
                    connections: The list of client sockets.
        Return: None

        This function takes in different sockets in order to close them.
    """
    for conn in connections:
        conn.close()
    server_socket.close()

if __name__ == "__main__":
    main()
