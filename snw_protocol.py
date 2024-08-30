#Code to handle SNW Communication over UDP
#References: https://realpython.com/python-sockets/

import socket

# Adjust this value based on your requirements
TIMEOUT = 1

CHUNK_SIZE = 1000

def send_packet_with_snw(sock, data, address):
    #Send data using the SNW protocol and wait for an acknowledgment
    
    # Divide data into chunks of 1000 bytes
    chunks = [data[i:i+1000] for i in range(0, len(data), 1000)]
    
    # Send total number of chunks first
    chunk_info = f"CHUNKS:{len(chunks)}".encode()
    try:
        sock.sendto(chunk_info, address)
        ack, _ = sock.recvfrom(1024)
        if ack.decode() != "ACK":
            return False
    except socket.timeout:
        return False

    # Send each chunk and wait for its acknowledgment
    for chunk in chunks:
        try:
            sock.sendto(chunk, address)
            ack, _ = sock.recvfrom(1024)
            if ack.decode() != "ACK":
                return False
        except socket.timeout:
            return False

    return True

def receive_packet_with_snw(sock):
    #Receive data using the SNW protocol and send an acknowledgment.
    
    # Receive total number of chunks first
    try:
        chunk_info, address = sock.recvfrom(1024)
        if not chunk_info.startswith(b"CHUNKS:"):
            raise ValueError("Unexpected data format received.")
    except socket.timeout:
        return b"", None

    # Acknowledge the chunk info
    send_ack(sock, address)
    
    total_chunks = int(chunk_info.split(b":")[1])
    data = b""
    
    # Receive each chunk and acknowledge its receipt
    for _ in range(total_chunks):
        try:
            chunk, _ = sock.recvfrom(1024)
            data += chunk
            send_ack(sock, address)
        except socket.timeout:
            return b"", None

    return data, address


def send_ack(sock, address, message="ACK"):
    sock.sendto(message.encode(), address)

def wait_for_ack(sock):
    #Wait for an acknowledgment
    try:
        ack, _ = sock.recvfrom(1024)
        return ack.decode() == "ACK"
    except socket.timeout:
        return False
