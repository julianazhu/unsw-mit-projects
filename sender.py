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
import stp


def send_file():
    addr = (receiver_host_IP, receiver_port)
    syn = stp.send_SYN(sock, addr)
    print("Sent {} SEQ: {} ACK: {}".format(syn.type, syn.sequence, syn.ack))
    synack = stp.receive_SYNACK(sock, syn)
    synack_ack = stp.send_incremented_ACK(sock, synack)
    print("Sent {} SEQ: {} ACK: {}".format(synack_ack.type, synack_ack.sequence, synack_ack.ack))
    push = stp.send_data(sock, synack, file_to_send)
    push.addr = synack.addr
    fin = stp.send_FIN(sock, push)
    print("Sent {} SEQ: {} ACK: {}".format(fin.type, fin.sequence, fin.ack))
    fin_ack = stp.receive_incremented_ACK(sock, fin)
    last_fin = stp.receive_FIN(sock, fin_ack)
    last_ack = stp.send_incremented_ACK(sock, last_fin)
    print("Sent {} SEQ: {} ACK: {}".format(last_ack.type, last_ack.sequence, last_ack.ack))
    print("Received final FIN and sent final ACK, TERMINATING")


# Get command line arguments
try:
    receiver_host_IP = sys.argv[1]
    receiver_port = int(sys.argv[2])
    file_to_send = sys.argv[3]
    # max_window_size = sys.argv[4]            # number of MSSs allowed in window
    # max_segment_size = sys.argv[5]           # bytes
    # timeout = sys.argv[6]                    # milliseconds

    # # PLD module command line arguments
    # pdrop = sys.argv[7]                      # probability of a segment drop
    # seed = int(sys.argv[8])                  # random number seed
except (IndexError, ValueError):
    print('Incorrect arguments. Usage: sender.py <receiver_host_ip>' 
        ' <receiver_port> <file.txt> not yet implemented - MWS> <MSS> <timeout> <pdrop> <seed>')
    sys.exit()

# Create the socket to internet, UDP
sock = socket.socket(socket.AF_INET,           # internet
                     socket.SOCK_DGRAM)        # UDP

send_file()
sock.close()