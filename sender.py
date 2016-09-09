# This programs implements a Simple Transport Protocol (STP) connection with a 
# receiver server over UDP, and sends a user-specified file to the server using
# a series of datagram packets. 
#
# Written by Juliana Zhu, z3252163 
# Written for COMP9331 16s2, Assignment 1. 
#
# Python 3.0


import sys
import socket
import datetime
import random


HEADER_SIZE = 9 # bytes


def send_SYN(sequence_number):
    header = create_header(sequence_number, "SYN", 5050) #temporary ack number
    segment = header
    # data = "The quick brown fox blahs"
    sock.sendto(segment, (receiver_host_IP, receiver_port))



# STP Header Format: 
#   Sequence No. (4 bytes), Acknowledgement No. (4 bytes)
#   Padding (4 bits), Flags (4 bits)
#
# 'segment_type' parameter accepts "SYN", "ACK", "SYNACK", "PUSH", "FIN"
def create_header(sequence_number, segment_type, ack_number, *data_length):
    sequence_number = format(sequence_number, '032b')
    ack_number = format(ack_number, '032b')
    if  segment_type == "SYN":
        flags = format(0b1000, '04b')
    elif segment_type == "SYNACK":
        flags = format(0b1100, '04b')
    elif segment_type == "ACK":
        flags = format(0b0100, '04b')
    elif segment_type == "PUSH":
        ack_number = format(ack_number + data_length, '032b')
        flags = format(0b0010, '04b')
    elif segment_type == "FIN":
        flags = format(0b0001, '04b')
    else:
        print("Unknown segment type:", segment_type)
        sys.exit()
    header_as_str = sequence_number + ack_number + '0000' + flags
    # Convert header to byte array:
    header = int(header_as_str, 2).to_bytes(len(header_as_str) // 8, byteorder='big')
    return header


# ==== MAIN ====
# Get command line arguments
try:
    receiver_host_IP = sys.argv[1]
    receiver_port = int(sys.argv[2])
    file_to_send = sys.argv[3]
    # max_window_size = sys.argv[4]            # bytes
    # max_segment_size = sys.argv[5]           # bytes
    # timeout = sys.argv[6]                    # milliseconds

    # # PLD module command line arguments
    # pdrop = sys.argv[7]                      # probability of a segment drop
    # seed = int(sys.argv[8])                  # random number seed
except (IndexError, ValueError):
    print('Incorrect arguments. Usage: sender.py <receiver_host_ip>' 
        ' <receiver_port> not yet implemented - <file.txt> <MWS> <MSS> <timeout> <pdrop> <seed>')
    sys.exit()

# Create the socket to internet, UDP
sock = socket.socket(socket.AF_INET,           # internet
                     socket.SOCK_DGRAM)        # UDP
sock.settimeout(5)                             # seconds
initial_sequence_number = 500 # Temp => change to random no. after testing
send_SYN(initial_sequence_number)

# Send file over UDP in chunks of data no larger than max_segment_size
# f = open(file_to_send, "rb")
# data = f.read(48) #+ headerFIRST
# while (data):
#     if(sock.sendto(data, (receiver_host_IP, receiver_port))):
#         print("sending...", data)
#         data = f.read(48) #+headerFIRST
# f.close
sock.close()