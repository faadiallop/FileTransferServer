""" File Transfer Client

This script allows the user to send files to the server.
"""
import socket
from os import path

HEADERSIZE = 10

def main():
    """ Parameters: None
        Return: None

        This function runs a TCP client to send files to a server.
    """
    try:
        ip_port = ("localhost", 5555)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect(ip_port)
        except ConnectionRefusedError:
            print("The server socket is not open!")
            return

        while True:

            file_name = str(input("File to transfer ('exit' to quit): "))

            if file_name == "exit":
                break

            if not path.exists(file_name) or path.isdir(file_name):
                print("Please enter a valid file path.")
                continue

            if not send_data(client_socket, file_name, True):
                break

            exception = False
            with open(file_name, "r", encoding="utf-8") as file:
                for line in file:
                    if not send_data(client_socket, line, False):
                        exception = True
                        break
            if exception:
                break

            if not send_data(client_socket, "done", False):
                break

            print(f"The file {(file.name)}",
                "has been sent to the server.")
    except KeyboardInterrupt:
        print("The client has been closed...")
    finally:
        send_data(client_socket, "exit", False)
        print("Closing client...")
        client_socket.close()

def send_data(client_socket, data, new_file):
    """ Parameters: client_socket: Socket to send data to. 
                    data: String that client is sending to server.
                    new_file: Boolean that indicates if this is a new
                    file or not.
        Return: Boolean that corresponds to whether the client was 
        successful in sending a message to the server.

        This function takes data and returns that data with a header.
    """
    try:
        client_socket.sendall(
            bytes(add_header(data, new_file), "utf-8")
            )
    except (BrokenPipeError, ConnectionResetError) as e:
        print(f"Received exception {type(e).__name__}",
              f"while trying to send '{data}' to the server!")
        return False
    return True

def add_header(data, new_file):
    """ Parameters: data: String that client is sending to server.
                    new_file: Boolean that indicates if this is a new
                    file or not.
        Return: String where first 9 characters correspond to the data
        size. The 10th character is a 1 or 0 corresponding to whether
        this is the start of a new file. The rest is the data of that
        is sent with the above header.
        This function takes data and returns that data with a header.
    """
    return f"{len(data):<{HEADERSIZE - 1}}{int(new_file)}{data}"

if __name__ == "__main__":
    main()
