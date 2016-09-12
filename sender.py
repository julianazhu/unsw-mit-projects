# This programs implements a Simple Transport Protocol (STP) connection with a 
# receiver server over UDP, and sends a user-specified file to the server using
# a series of datagram packets. 
#
# The connection establishment and teardown segments from the Sender bypass the 
# PLD module and are not dropped.
#
# Written by Juliana Zhu, z3252163 
# Written for COMP9331 16s2, Assignment 1. 
#
# Python 3.0


import sys
import socket
from stp import Connection                # helper

# Get command line arguments
try:
    receiver_host_IP = sys.argv[1]
    receiver_port = int(sys.argv[2])
    file_to_send = sys.argv[3]
    max_window_size = sys.argv[4]            # bytes
    max_segment_size = sys.argv[5]           # bytes
    timeout = sys.argv[6]                    # milliseconds

    # # PLD module command line arguments
    pdrop = sys.argv[7]                      # probability of a segment drop
    seed = int(sys.argv[8])                  # random number seed
except (IndexError, ValueError):
    print('Incorrect arguments. Usage: sender.py <receiver_host_ip>' 
        ' <receiver_port> <file.txt> <MWS> <MSS> <timeout> <pdrop> <seed>')
    sys.exit()

# Create the socket port, create the STP connection, send the file and close.
sock = socket.socket(socket.AF_INET,           # internet
                     socket.SOCK_DGRAM,
                     socket.IPPROTO_UDP)       # UDP
connection = Connection(sock, 
                        'Sender_log.txt',
                        None, 
                        (receiver_host_IP, receiver_port), 
                        max_window_size, 
                        max_segment_size, 
                        timeout,
                        (pdrop, seed))
connection.send_file(file_to_send)
sock.close()