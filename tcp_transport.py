#Code to handle TCP protocol Communication
# References: https://www.geeksforgeeks.org/socket-programming-python/, https://realpython.com/python-sockets/
import socket

def create_tcp_server_socket(host, port, listen=5):
    #Creates a TCP server socket and binds it to the given host and port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind((host, port))
    s.listen(listen)
    return s

def create_tcp_client_socket(host, port):
    #Creates a TCP client socket and connects it to the given host and port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s

def send_data(tcp_socket, data):
    #Sends the data over the given TCP socket
    total_sent = 0
    while total_sent < len(data):
        sent = tcp_socket.send(data[total_sent:])
        if sent == 0:
            raise Exception("Socket connection broken")
        total_sent += sent

def receive_data(tcp_socket, buffer_size=65507, exact_size=None):
    #Receives data over the given TCP socket. If exact_size is provided, reads that many bytes
    data = b''
    while True:
        chunk = tcp_socket.recv(buffer_size if not exact_size else min(buffer_size, exact_size))
        if chunk == b'':
            raise Exception("Socket connection broken")
        data += chunk
        if exact_size:
            exact_size -= len(chunk)
            if exact_size <= 0:
                break
        elif len(chunk) < buffer_size:
            break
    return data

def close_socket(tcp_socket):
    #Closes the given TCP socket
    tcp_socket.close()
