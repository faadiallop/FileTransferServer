""" Multi-Threaded File Transfer Server

This script allows the user to create a server that listens
for incoming file transfers.
If formatted corrected this server can also be interacted with through
programs such as netcat.
This program is an implementation of the File Transfer Protocol.
"""
import socket
import select
import argparse
import threading

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
        print_lock = threading.Lock()

        args = process_arguments()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("", listening_port))

        server_socket.listen()
        print(f"Listening on port {listening_port}...")

        max_connections = args.max_connections[0]
        connections_semaphore = threading.Semaphore(max_connections)
        while True:
            ready_to_read, _, _ = select.select([server_socket], [], [])
            if ready_to_read:
                if threading.active_count() - 1 < max_connections:
                    connection, address = server_socket.accept()
                    try:
                        connection.sendall(bytes("Accepted", "utf-8"))
                    except (BrokenPipeError, ConnectionResetError) as e:
                        print(f"Received exception {type(e).__name__}",
                            "while trying to send 'Accepted' to the server!")
                        continue
                    client_print(address, "Connection has been accepted!")
                    thread = threading.Thread(
                        target=data_processing,
                        args=(connection,
                              address,
                              print_lock,
                              connections_semaphore)
                        )
                    thread.start()
                else:
                    connection, address = server_socket.accept()
                    try:
                        connection.sendall(bytes("Failed", "utf-8"))
                    except (BrokenPipeError, ConnectionResetError) as e:
                        print(f"Received exception {type(e).__name__}",
                            "while trying to send 'Failed' to the server!")
                        continue
                    client_print(address, "Attempted to connect but the " +
                                 "maximum connections have been reached")
    except KeyboardInterrupt:
        print("The server has been closed...")
    finally:
        print("Closing server...")
        server_socket.close()

def client_print(address, message):
    """ Parameters: address: Tuple of client IP address & port number.
                    message: String the client is sending to the server.
        Return: None
        
        Prints message string the address prepended.
    """
    print(f"{address}: {message}")

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

def data_processing(connection, address, print_lock, connections_semaphore):
    """ Parameters: connection: A client socket.
                    address: Tuple of Client IP address. 
                    print_lock: Lock for print statements.
                    num_conn_lock: Lock for num_conn variable
        Return: None

        This function processes the file bytes from the client to copy
        that file to a file called {file name}.output.
    """

    with connections_semaphore:
        print("Number of available connections:",
              f"{connections_semaphore._value}")
        with connection:
            buffer_size = 16
            headered = True
            buffer = ""
            data = ""
            file_name = ""
            while True:
                try:
                    data += connection.recv(buffer_size).decode()
                except (BrokenPipeError, ConnectionResetError) as e:
                    print(f"Received exception {type(e).__name__}",
                        f"while trying to receive data from the {address}")
                    break

                if headered:
                    header = data[:HEADERSIZE]
                    # Last number identifies if this is a new file
                    data_size = int(header[:-1])
                    new_file = bool(int(header[-1]))
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
                        with print_lock:
                            client_print(address,
                                            f"File written to {file_name}")
                    elif new_file:
                        file_name = buffer + ".output"
                        new_file = False
                    else:
                        with open(file_name, "a", encoding="utf-8") as file:
                            file.write(buffer)

                    headered = True
                    buffer = ""
        with print_lock:
            client_print(address, "Client has exited!")
        print("Number of available connections:",
              f"{connections_semaphore._value + 1}")

if __name__ == "__main__":
    main()
