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
from stp_headers import receive_segment      # helper
from stp_headers import create_header       # helper
from stp_headers import interpret_header    # helper


def send_SYN(sequence_number):
    header = create_header("SYN", sequence_number, 0)
    segment = header
    # data = "The quick brown fox blahs"
    sock.sendto(segment, (receiver_host_IP, receiver_port))

def receive_SYNACK(expected_ack):
    return_addr, segment_type, received_sequence_no, received_ack_no = receive_segment(sock)
    if segment_type == "SYNACK" and received_ack_no == expected_ack:
        return return_addr, received_sequence_no, received_ack_no
    else:
        wait_for_ACK(expected_ack)

def send_ACK(return_addr, ack_number, sequence_number):
    header = create_header("ACK", sequence_number, ack_number+1)
    segment = header
    sock.sendto(segment, (return_addr))

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
# sock.settimeout(5)                             # seconds
sequence_number = 0 # Temp => change to random no. after testing
send_SYN(sequence_number)
sequence_number += 1
return_addr, received_sequence_no, received_ack_no = receive_SYNACK(sequence_number)
print("Successfully received SYNACK")
send_ACK(return_addr, received_sequence_no, sequence_number)
# Send file over UDP in chunks of data no larger than max_segment_size
# f = open(file_to_send, "rb")
# data = f.read(48) #+ headerFIRST
# while (data):
#     if(sock.sendto(data, (receiver_host_IP, receiver_port))):
#         print("sending...", data)
#         data = f.read(48) #+headerFIRST
# f.close
# sock.close()