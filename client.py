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
        client_socket.connect(ip_port)

        while True:
            file_name = str(input("File to transfer ('exit' to quit): "))
            client_socket.sendall(bytes(add_header(file_name), "UTF-8"))

            if file_name == "exit": break

            if not path.exists(file_name) or path.isdir(file_name):
                print("Please enter a valid file path.")
                continue

            with open(file_name, "r") as file:
                for line in file:
                    client_socket.sendall(bytes(add_header(line), "UTF-8"))

            print(f"The file {(file.name)}", 
                "has been sent to the server.")
    except KeyboardInterrupt:
        print("The client has been closed...")
        #ADD A CHECK FOR IF THE SERVER CLOSE PREMATURELY
    finally:
        print("Closing client...")
        client_socket.sendall(bytes(add_header("exit"), "UTF-8"))
        client_socket.close()

def add_header(packet):
    print(len(packet))
    return f"{len(packet):<{HEADERSIZE}}{packet}"

if __name__ == "__main__":
    main()