# This helper file contains all of the basic functions required for Simple
# Transport Protocol (STP) including functions for sending and receiving 
# SYN, SYNACK, ACK, PUSH and FIN type segments. 
#
#
# Written by Juliana Zhu, z3252163 
# Written for COMP9331 16s2, Assignment 1. 
#
# Python 3.0


import struct
import sys
from stp_segment import Segment                   # helper


HEADER_SIZE = 9 # bytes


def receive_segment(sock):
    while True:
        data, addr = sock.recvfrom(48 + HEADER_SIZE)
        header = data[:HEADER_SIZE+1]
        data = data[HEADER_SIZE:]
        segment_type, sequence_number, ack_number = interpret_header(header)
        segment = Segment(segment_type, sequence_number, ack_number, data, addr)
        print("Received TYPE: {}, SEQ:{}, ACK: {}".format(segment.type, segment.sequence, segment.ack))
        return segment

def interpret_header(header):
    # 'Struct.unpack' translates byte array to a tuple initially.
    sequence_number = struct.unpack(">i", header[:4])
    sequence_number = sequence_number[0]
    ack_number = struct.unpack(">i", header[4:8])
    ack_number = ack_number[0]
    flags = header[8]
    if flags == 0b1000:
        segment_type = "SYN"
    elif flags == 0b1100:
        segment_type = "SYNACK"
    elif flags == 0b0100:
        segment_type = "ACK"
    elif flags == 0b0010:
        segment_type = "PUSH"
    elif flags == 0b0001:
        segment_type = "FIN"
    else:
        print("Unknown segment type:", flags)
        sys.exit()
    return segment_type, sequence_number, ack_number

def send_SYN(sock, addr):
    sequence_number = 0 # Temp => change to random no. after testing
    ack_number = 0
    segment = Segment("SYN", sequence_number, ack_number, '')
    sock.sendto(segment.package, (addr))
    return segment

def receive_SYN(sock):
    segment = receive_segment(sock)
    if segment.type == "SYN":
        return segment
    else:
        receive_SYN(expected_ack)

def send_SYNACK(sock, prior):
    sequence_number = 0 # Temp => change to random no. after testing
    segment = Segment("SYNACK", prior.ack, prior.sequence + 1, '')
    print("prior address = ", prior.addr)
    sock.sendto(segment.package, prior.addr)
    return segment

def receive_SYNACK(sock, prior):
    segment = receive_segment(sock)
    if segment.type == "SYNACK" and segment.ack == prior.sequence + 1:
        return segment
    else:
        receive_SYNACK(expected_ack)

def send_incremented_ACK(sock, prior): 
    segment = Segment("ACK", prior.ack, prior.sequence + 1, '')
    sock.sendto(segment.package, prior.addr)
    return segment

def receive_incremented_ACK(sock, prior):
    segment = receive_segment(sock)
    print("expected_ack = {}, received_ack_no= {}".format(prior.sequence + 1, segment.ack))
    if segment.type == "ACK" and segment.ack == prior.sequence + 1:
        return segment
    else:
        receive_incremented_ACK(sock, prior)

def send_ACK(sock, prior): 
    segment = Segment("ACK", prior.ack, prior.sequence, '')
    sock.sendto(segment.package, prior.addr)
    return segment

def receive_ACK(sock, prior):
    print("Expected Ack =", prior.sequence)
    segment = receive_segment(sock)
    print("prior sequence = ")
    if segment.type == "ACK" and segment.ack == prior.sequence:
        return segment
    else:
        receive_ACK(prior)

def send_data(sock, prior, file_to_send):
    prior.sequence += 1
    f = open(file_to_send, "rb")
    data = f.read(48)
    while (data):
        segment = Segment("PUSH", prior.ack + len(data), prior.sequence, data)
        print("Sent PUSH. SEQ {}, ACK: {}:".format(segment.sequence, segment.ack))
        print("segment header length = ", len(segment.package))
        if(sock.sendto(segment.package, prior.addr)):
            prior = receive_ACK(sock, segment)
            data = f.read(48)
        print("--------------------------------------")
    f.close()
    return segment

def receive_data(sock, prior, filename):
    prior.sequence += 1
    assembled_file = "" 
    while True:
        segment = receive_segment(sock)
        print("expected_ack= {}, received_ack_no= {}".format(prior.sequence, segment.ack))
        if segment.type == "PUSH" and segment.ack == prior.sequence:
            assembled_file += segment.data
            print("ADDED: ", segment.data)
            prior = send_ACK(sock, segment)
        elif segment.type == "FIN" and segment.ack == prior.sequence:
            with open(filename, 'w') as f:
                f.write(assembled_file)
                f.close()
            return segment
        print("--------------------------------------")

def send_FIN(sock, prior):
    segment = Segment("FIN", prior.sequence + 1, prior.ack, '')
    sock.sendto(segment.package, prior.addr)
    return segment

def receive_FIN(sock, prior):
    segment = receive_segment(sock)
    print("expected_ack= {}, received_ack_no= {}".format(prior.ack, segment.ack))
    if segment.type == "FIN" and segment.ack == prior.ack:
        return segment
    else:
        receive_FIN(sock, prior)