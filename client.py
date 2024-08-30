# CLIENT CODE #
# Name: Raghavendra Vamshi Teja Chathurajupalli
# Project 1

# Description: Code behaves as Client. The client uses commands get, put and quit. It uses get to request friles from server. In case the file is already available with cache, it recives file from cache else the cache itself sends the request to server and returns the file to client.

# Execution Procedure: Open terminal/cmd, change to the directory in which cache.py file is present, then run python3 cache.py <cache_port> <server_host> <server_port> 

# Initializing necessary headers

import sys
import socket
import os
from snw_protocol import send_packet_with_snw, receive_packet_with_snw
import tcp_transport as TCP

file_directory = "client_files"

#Section to handle SNW Communication
def SNW_handle_command(command, cache_socket, server_socket, cache_address, server_address):
    if command.startswith("get "):
        filename = command[4:]
        send_packet_with_snw(cache_socket, command.encode(), cache_address) # Send request: get <filename.txt>
        try:
            data, _ = receive_packet_with_snw(cache_socket) #Receive initial info
            if data.startswith(b"from"):
                print("Server response: File delivered",data.decode())
                file_data, _ = receive_packet_with_snw(cache_socket) # Save filedata received
                with open(filename, 'wb') as f:
                    f.write(file_data)
                print(f"File {filename} received and saved.") # Confirm user
            else:
                print("Did not receive data. Terminating")
        except socket.timeout:
            print("Did not receive ACK. Terminating")
            send_packet_with_snw(server_socket, command.encode(), server_address)
            try:
                data, _ = receive_packet_with_snw(server_socket)
                if data.startswith(b"from"):
                    print("Server response: File delivered",data.decode())
                    file_data, _ = receive_packet_with_snw(server_socket)
                    with open(filename, 'wb') as f:
                        f.write(file_data)
                    print(f"File {filename} received and saved.")

                elif data.startswith(b"The file"):
                    print("File not found on server or cache")
                else:
                    print("Did not receive data. Terminating")
            except socket.timeout:
                print("Did not receive ACK. Terminating ")

    elif command.startswith("put "):
        filename = command[4:]
        if not os.path.isfile(filename):
           print("File does not exist.")
           return
        with open(filename, 'rb') as f:
           file_data = f.read()
        send_packet_with_snw(server_socket, command.encode(), server_address)
        send_packet_with_snw(server_socket, file_data, server_address)
        print("Awaiting Server Response")
        ackSNW, _=receive_packet_with_snw(server_socket)
        print("Server Response:", ackSNW.decode())

    elif command.startswith("quit"):
        print("Exiting Program!")
        sys.exit(0)

    else:
        print("Invalid command. Please enter 'get <filename>' or 'put <filename>'.")

def main():
    if len(sys.argv) != 6:
        print("Usage: python client.py <server_host> <server_port> <cache_host> <cache_port> <Protocol>")
        sys.exit(1)

#Handling command line arguments
SERVER_HOST = sys.argv[1] #'localhost' 
SERVER_PORT = int(sys.argv[2]) #10000
CACHE_HOST =  sys.argv[3]
CACHE_PORT =  int(sys.argv[4])
protocolType= sys.argv[5]

if not os.path.exists(file_directory):
    os.makedirs(file_directory)

os.chdir(file_directory)  # Changes current saving directory of file to cache_files

#Handling for TCP 

if protocolType == 'tcp':

    while True:
        command = input("Enter Command: ")
        # References: https://docs.python.org/3/howto/sockets.html, https://realpython.com/python-sockets/
        # Handling GET command
        if command.startswith("get "):   # Check for Get command
            filename = command.replace("get ", "") 
            cache_socket = TCP.create_tcp_client_socket(CACHE_HOST, CACHE_PORT) # Create TCP Socket
            TCP.send_data(cache_socket, command.encode('utf-8')) #Send data, in this case get <filename.txt>
            data = TCP.receive_data(cache_socket) # Store file data received from Socket
            file_data, ack_msg = data.rsplit(b"\n", 1)
            # Section to save the received file
            with open(filename, 'wb') as f:
                f.write(file_data)
            print(ack_msg.decode()) # Decode the Acknowledgment
            TCP.close_socket(cache_socket)
        # Handling PUT command
        elif command.startswith("put "): #Check if command starts with get
            filename = command.replace("put ", "")
            if not os.path.exists(filename):
                print("File does not exist!")
                continue
            server_socket = TCP.create_tcp_client_socket(SERVER_HOST, SERVER_PORT)
            with open(filename, 'rb') as f:
                file_data = f.read()
            
            TCP.send_data(server_socket, (filename + "|").encode('utf-8') + file_data) # Sending filename as a header prior to sending the actual file content
            print("Awaiting Server Response")
            ack_msg = TCP.receive_data(server_socket).decode('utf-8')
            print("Server Response:", ack_msg)
            TCP.close_socket(server_socket)
        elif command.startswith("quit"): #To handle quit command, shuts down client only, not cache or server
            print("Exiting Program!")
            sys.exit(0)
        else:
            print("Invalid command!") # If neither of the commands match, this is used as catch all
            # End of TCP Definition
# Handling for SNW
elif protocolType == 'snw':
     # References: https://docs.python.org/3/library/socket.html, https://realpython.com/python-sockets/
     cache_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Taking BSD socket library access and creating one to connect with cache over UDP with socket type as SOCK_DGRAM used for unreliable or connectionless types of communication
     cache_socket.settimeout(1) #Timeout of 1 second for no reply

     server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Taking BSD socket library access and creating one to connect with Server over UDP with socket type as SOCK_DGRAM used for unreliable or connectionless types of communication
     server_socket.settimeout(1) #Timeout of 1 second for no reply

     while True:
         command = input("Enter command: ")
         SNW_handle_command(command, cache_socket, server_socket, (CACHE_HOST, CACHE_PORT), (SERVER_HOST, SERVER_PORT))

     
if __name__ == "__main__":
    main()  #Call Main

    


   




