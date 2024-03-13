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
    listening_port = 5555
    print_lock = threading.Lock()
    args = process_arguments()
    max_connections = args.max_connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    with server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("", listening_port))

        server_socket.listen()
        print(f"Listening on port {listening_port}...")

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
                            max_connections),
                        daemon=True
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
                        default=3,
                        help=help_max_conn
                        )
    return parser.parse_args()

def data_processing(connection, address, print_lock, max_connections):
    """ Parameters: connection: A client socket.
                    address: Tuple of Client IP address. 
                    print_lock: Lock for print statements.
        Return: None

        This function processes the file bytes from the client to copy
        that file to a file called {file name}.output.
    """
    print("Number of available connections:",
            f"{max_connections - (threading.active_count() - 1)}")
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
                        message = f"{file_name} written to {file_name}.output"
                        client_print(address, message)
                elif new_file:
                    file_name = buffer
                    new_file = False
                else:
                    with open(file_name + ".output",
                                "w+",
                                encoding="utf-8") as file:
                        file.write(buffer)

                headered = True
                buffer = ""
    with print_lock:
        client_print(address, "Client has exited!")
    # Minus 2 to account for the closing of current thread
    print("Number of available connections:",
            f"{max_connections - (threading.active_count() - 2)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("The server has been closed...")
    finally:
        print("Closing server...")
