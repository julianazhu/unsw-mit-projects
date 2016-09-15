# This class module defines a "segment" for use with Simple Transport Protocol (STP)
# where each segment consists of a 9 byte header and a byte array of data 
# (length defined by the user) that is designed to be passed between a STP 
# sender and receiver. 
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


import sys
import struct


class Segment:
    def __init__(self, segment_type, sequence_number, ack_number, data, addr):
        self.type = segment_type
        self.sequence = sequence_number
        self.ack = ack_number
        self.data = data
        self.header = self.create_header()
        try:
            self.package = self.header + bytearray(data, 'ascii')
        except:
            self.package = self.header + data
        self.time = 0
        self.addr = addr

    def init_from_received(self, header_size, package, addr):
        header = package[:header_size + 1]
        data = package[header_size:]
        segment_type, sequence_number, ack_number = Segment.interpret_header(None, header)
        segment = Segment(segment_type, sequence_number, ack_number, data, addr)
        return segment

    # 'self.type' parameter accepts "SYN", "ACK", "SYNACK", "PUSH", "FIN"
    def create_header(self):
        sequence_number = format(self.sequence, '032b')
        ack_number = format(self.ack, '032b')
        padding = format(0, '04b')

        if self.type == "S":
            flags = format(0b1000, '04b')
        elif self.type == "A":
            flags = format(0b0100, '04b')
        elif self.type == "SA":
            flags = format(0b1100, '04b')
        elif self.type == "P":
            flags = format(0b0010, '04b')
        elif self.type == "F":
            flags = format(0b0001, '04b')
        elif self.type == "FA":
            flags = format(0b0101, '04b')
        else:
            print("Unknown segment type:", self.type)
            sys.exit()

        header_as_str = sequence_number + ack_number + padding + flags
        # Convert header to byte array:
        return int(header_as_str, 2).to_bytes(len(header_as_str) // 8, byteorder='big')

    def interpret_header(self, header):
        # 'Struct.unpack' translates byte array to a tuple initially.
        sequence_number = struct.unpack(">i", header[:4])
        sequence_number = sequence_number[0]
        ack_number = struct.unpack(">i", header[4:8])
        ack_number = ack_number[0]
        flags = header[8]
        if flags == 0b1000:
            segment_type = "S"
        elif flags == 0b1100:
            segment_type = "SA"
        elif flags == 0b0100:
            segment_type = "A"
        elif flags == 0b0010:
            segment_type = "P"
        elif flags == 0b0001:
            segment_type = "F"
        elif flags == 0b0101:
            segment_type = "FA"
        else:
            print("Unknown segment type:", flags)
            sys.exit()
        return segment_type, sequence_number, ack_number