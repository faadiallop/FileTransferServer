""" File Transfer Server

This script allows the user to send files to the server.
Specifically, the user can send files the server created by the
corresponding server.py script.
"""
import socket
from os import path

HEADERSIZE = 10

def main():
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
            if not path.exists(file_name) or path.isdir(file_name):
                print("Please enter a valid file path.")
                continue

            if not send_data(client_socket, file_name, True): break

            if file_name == "exit": break

            exception = False
            with open(file_name, "r") as file:
                for line in file:
                    if not send_data(client_socket, line, False): 
                        exception = True 
                        break
            if exception: break

            print(f"The file {(file.name)}", 
                "has been sent to the server.")
    except KeyboardInterrupt:
        print("The client has been closed...")
        #ADD A CHECK FOR IF THE SERVER CLOSE PREMATURELY
    finally:
        if not send_data(client_socket, "exit", False): pass
        print("Closing client...")
        client_socket.close()

def send_data(client_socket, data, new_file):
    try:
        client_socket.sendall(
            bytes(add_header(data, new_file), "UTF-8")
            )
    except (BrokenPipeError, ConnectionResetError) as e:
        print(f"Received exception {type(e).__name__}", 
              f"while trying to send '{data}' to the server!")
        return False 
    return True

def add_header(data, new_file):
    return f"{len(data):<{HEADERSIZE - 1}}{int(new_file)}{data}"

if __name__ == "__main__":
    main()