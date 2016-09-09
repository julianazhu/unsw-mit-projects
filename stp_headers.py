# This helper file contains the functions that create and interpret headers
# for the Simple Transport Protocol (STP).
#
# STP Header Format: 
#   Sequence No. (4 bytes), Acknowledgement No. (4 bytes)
#   Padding (4 bits), Flags (4 bits)
#
#
# Written by Juliana Zhu, z3252163 
# Written for COMP9331 16s2, Assignment 1. 
#
# Python 3.0


import struct


HEADER_SIZE = 9 # bytes


def receive_segment(sock):
    while True:
        data, return_addr = sock.recvfrom(48 + HEADER_SIZE)
        header = data[:HEADER_SIZE]
        data = data[HEADER_SIZE+1:]
        print("Received File => Header: {} Data: {}".format(header, data))
        segment_type, received_sequence_no, received_ack_no = interpret_header(header)
        print("Unpacked =>  TYPE: {}, SEQ:{}, ACK:{}"
            .format(segment_type, received_sequence_no, received_ack_no))
        return return_addr, segment_type, received_sequence_no, received_ack_no

# 'segment_type' parameter accepts "SYN", "ACK", "SYNACK", "PUSH", "FIN"
def create_header(segment_type, sequence_number, ack_number, *data_length):
    sequence_number = format(sequence_number, '032b')
    ack_number = format(ack_number, '032b')
    if  segment_type == "SYN":
        flags = format(0b1000, '04b')
    elif segment_type == "ACK":
        flags = format(0b0100, '04b')
    elif segment_type == "SYNACK":
        flags = format(0b1100, '04b')
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
    elif flags == 0b0001:
        segment_type = "FIN"
    else:
        print("Unknown segment type:", segment_type)
        sys.exit()
    return segment_type, sequence_number, ack_number
