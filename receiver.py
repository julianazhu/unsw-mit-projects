# Server to receive messages over Simple Transport Protocol (STP). The server 
# sits in an infinite loop listening for a file in sent via UDP packets from 
# an STP client. The server then reassembles the data and writes it to file 
# under the user-specified filename.
#
# Written by Juliana Zhu, z3252163
# Written for COMP9331 16s2, Assignment 1. 
#
# Python 3.0


import sys
import socket
from connection import Connection

# Command line arguments
try:
    receiver_port = int(sys.argv[1])
    filename = sys.argv[2]
except (IndexError, ValueError):
    print("Incorrect arguments. Usage: receiver.py <receiver_port> <file.txt>")
    sys.exit()

# Open the listening socket port, create the STP connection, receive the file and close.
sock = socket.socket(socket.AF_INET,                 # internet
                            socket.SOCK_DGRAM,
                            socket.IPPROTO_UDP)      # UDP
sock.bind(('127.0.0.1', receiver_port))
connection = Connection(sock, 'Receiver_log.txt',('127.0.0.1', receiver_port))
connection.receive_file(filename)
sock.close()
