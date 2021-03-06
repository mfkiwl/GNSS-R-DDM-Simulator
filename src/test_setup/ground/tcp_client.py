#!/usr/bin/env python3

import struct
import socket
import pickle
import sys
from time import sleep

import telemetry

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def main():
    telemetry_processor = telemetry.processor()

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "192.168.60.82"
    port = 8887

    try:
        soc.connect((host, port))
    except:
        print("Connection error")
        sys.exit()

    print("Enter 'quit' to exit")
    message = input(" -> ")

    while message != 'quit':

        if message == "START":
            while True:
                soc.sendall("GET_TM".encode("utf8"))
                res = soc.recv(5120).decode("utf8")
                if res == 'NEW_DATA':
                    data = recv_msg(soc)
                    tm = pickle.loads(data)
                    telemetry_processor.load_telemetry(tm)
                    telemetry_processor.plot_telemetry()
                elif res == 'NO_NEW_DATA':
                    pass
                    sleep(0.4)

        else:
            soc.sendall(message.encode("utf8"))
            res = soc.recv(5120).decode("utf8")
            if res == "-":
                pass        # null operation

        message = input(" -> ")

    soc.send(b'--QUIT--')

if __name__ == "__main__":
    main()
