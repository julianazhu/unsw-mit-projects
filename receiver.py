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
import struct


RECEIVER_IP = "127.0.0.1"
HEADER_SIZE = 9 # bytes


def interpret_header(header):
    sequence_number = header[:4]
    sequence_number = struct.unpack(">i", sequence_number)
    # 'Struct.unpack' translates the byte array to a tuple, hence need to 
    # further unpack.
    sequence_number = sequence_number[0]
    ack_number = header[4:8]
    ack_number = struct.unpack(">i", ack_number)
    ack_number = ack_number[0]
    flags = header[8]
    if flags == 0b1000:
        segment_type = "SYN"
    elif flags == 0b1100:
        segment_type == "SYNACK"
    elif flags == 0b0100:
        segment_type = "ACK"    
    elif flags == 0b0010:
        segment_type = "PUSH"            
    elif flags == 0b0001:
        segment_type = "FIN"    
    else:
        print("Unknown segment type:", segment_type)
        sys.exit()
    print("segment_type:", segment_type)
    return sequence_number, ack_number, segment_type

# def generate_ack(sequence_number, ack_number):
#     sock.sendto(segment, (receiver_host_IP, receiver_port))

# MAIN:
# Command line arguments
try:
    receiver_port = int(sys.argv[1])
    filename = sys.argv[2]
except (IndexError, ValueError):
    print("Incorrect arguments. Usage: receiver.py <receiver_port> <file.txt>")
    sys.exit()

# Open the listening socket port.
sock = socket.socket(socket.AF_INET,      # internet
                            socket.SOCK_DGRAM)   # UDP
sock.bind((RECEIVER_IP, receiver_port))


# Receive file and write to specified filename.
while True:
    data, addr = sock.recvfrom(48+HEADER_SIZE)
    header = data[:HEADER_SIZE]
    data = data[HEADER_SIZE+1:]
    print("Received File => Header: {} Data: {}".format(header, data))
    sequence_number, ack_number, segment_type = interpret_header(header)
    # if segment_type == "SYN":
    #     generate_ack(sequence_number, ack_number)

    # with open(filename, 'a') as f:
        # f.write(data)
    # f.close()

