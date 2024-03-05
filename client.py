""" File Transfer Server

This script allows the user to send files to the server.
Specifically, the user can send files the server created by the
corresponding server.py script.
"""
import socket
import argparse
from os import path

def main():
    ip_port = ("localhost", 5555)

    parser = argparse.ArgumentParser(
        description="Runs a client for file transfers"
        )
    parser.add_argument("file",
                        metavar="file",
                        type=argparse.FileType("r", 1024)
                        )
    args = parser.parse_args()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(ip_port)

    with args.file as file:
        for line in file:
            client_socket.send(bytes(line, "UTF-8"))
    
        print(f"The file {path.basename(file.name)}", 
              "has been sent to the server.")
        
    client_socket.close()

if __name__ == "__main__":
    main()