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
import datetime
from stp_headers import create_header       # helper
from stp_headers import interpret_header    # helper


RECEIVER_IP = "127.0.0.1"
HEADER_SIZE = 9 # bytes

def generate_synack(sender_addr, sender_sequence_number):
    sequence_number = 0 # Temp => change to random no. after testing
    ack_number = sender_sequence_number + 1 
    header = create_header("SYNACK", sequence_number, ack_number)
    segment = header
    sock.sendto(segment, (sender_addr))
    pass


# ===== MAIN =====
# Command line arguments
try:
    receiver_port = int(sys.argv[1])
    filename = sys.argv[2]
except (IndexError, ValueError):
    print("Incorrect arguments. Usage: receiver.py <receiver_port> <file.txt>")
    sys.exit()

# Open the listening socket port.
sock = socket.socket(socket.AF_INET,                # internet
                            socket.SOCK_DGRAM)      # UDP
sock.bind((RECEIVER_IP, receiver_port))


# Receive file and write to specified filename.
while True:
    data, sender_addr = sock.recvfrom(48+HEADER_SIZE)
    header = data[:HEADER_SIZE]
    data = data[HEADER_SIZE+1:]
    print("Received File => Header: {} Data: {}".format(header, data))
    segment_type, sender_sequence_number, sender_ack_number = interpret_header(header)
    generate_synack(sender_addr, sender_sequence_number)
    # if segment_type == "SYN":
    #     generate_ack(sequence_number, ack_number)

    # with open(filename, 'a') as f:
        # f.write(data)
    # f.close()

