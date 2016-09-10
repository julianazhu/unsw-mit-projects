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
import stp

RECEIVER_IP = "127.0.0.1"


def receive_file():
    syn = stp.receive_segment(sock)
    synack = stp.send_SYNACK(sock, syn)
    print("Sent {} SEQ: {} ACK: {}".format(synack.type, synack.sequence, synack.ack))
    synack_ack = stp.receive_incremented_ACK(sock, synack)
    push = stp.receive_data(sock, synack, filename)
    ack = stp.send_incremented_ACK(sock, push)
    ack.addr = push.addr
    print("Sent {} SEQ: {} ACK: {}".format(ack.type, ack.sequence, ack.ack))
    fin = stp.send_FIN(sock, ack)
    print("Sent {} SEQ: {} ACK: {}".format(fin.type, fin.sequence, fin.ack))
    fin.addr = ack.addr
    stp.receive_incremented_ACK(sock, fin)
    print("All done, terminating")

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
receive_file()
sock.close()
