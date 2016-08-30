# This program sends ping requests to port specified by the user. 
# Written by Juliana Zhu, z3252163 
# Written for COMP9331 16s2, Assignment 1. 


import sys
import socket
import datetime


BUFFER = 24                                  # bytes


# Command line arguments
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
except IndexError:
    print('Incorrect arguments. Usage: sender.py <receiver_host_ip>' 
        ' <receiver_port> <file.txt> <MWS> <MSS> <timeout> <pdrop> <seed>')
    sys.exit()


# Create the socket to internet, UDP
sock = socket.socket(socket.AF_INET,            # internet
                     socket.SOCK_DGRAM)         # UDP
sock.settimeout(1)                              # second/s


# Send file over UDP in chunks of data no larger than max_segment_size
f = open(file_to_send, "rb")
data = f.read(BUFFER)
while (data):
    if(sock.sendto(data, (receiver_host_IP, receiver_port))):
        print("sending...")
        data = f.read(24)
sock.close()
f.close









# # Sent the sequence of pings. 
# for sequence_number in range(10):
#     send_time = datetime.datetime.now()
#     message = "PING " + str(sequence_number) + " " + str(send_time) 
#     try:
#         sock.sendto(message, (receiver_host_IP, receiver_port))
#         if sock.recvfrom(1024):
#             rtt = datetime.datetime.now() - send_time
#             print("ping to {}, seq {}, rtt = {}ms".format(host, sequence_number, rtt.microseconds / 1000))
#     except socket.timeout:
#         continue