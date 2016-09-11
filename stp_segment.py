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



class Segment:
    def __init__(self, segment_type, sequence_number, ack_number, data, *addr):
        self.type = segment_type
        self.sequence = sequence_number
        self.ack = ack_number
        self.header = self.create_header()
        try:
            data = str(data, "ascii")
        except:
            pass
        self.data = data
        try:
            self.addr = addr
            self.addr = self.addr
        except:
            pass
        self.package = self.header + bytearray(data, 'ascii')
        self.log = self.create_log_entry()

    # 'self.type' parameter accepts "SYN", "ACK", "SYNACK", "PUSH", "FIN"
    def create_header(self):
        sequence_number = format(self.sequence, '032b')
        ack_number = format(self.ack, '032b')
        padding = format(0, '04b')

        if self.type == "SYN":
            flags = format(0b1000, '04b')
        elif self.type == "ACK":
            flags = format(0b0100, '04b')
        elif self.type == "SYNACK":
            flags = format(0b1100, '04b')
        elif self.type == "PUSH":
            flags = format(0b0010, '04b')
        elif self.type == "FIN":
            flags = format(0b0001, '04b')
        else:
            print("Unknown segment type:", self.type)
            sys.exit()

        header_as_str = sequence_number + ack_number + padding + flags
        # Convert header to byte array:
        return int(header_as_str, 2).to_bytes(len(header_as_str) // 8, byteorder='big')
    
    def create_log_entry(self):
        if self.type == "SYN":
            code = 'S'
        elif self.type == "ACK":
            code = 'A'
        elif self.type == "SYNACK":
            code = 'SA'
        elif self.type == "PUSH":
            code = 'D'
        elif self.type == "FIN":
            code = 'F'

        code = '{:>4}'.format(code)
        sequence_number = '{:6}'.format(int(self.sequence))
        data_length = '{:6}'.format(len(self.data))
        ack_number = '{:6}'.format(int(self.ack))
        return code + sequence_number + data_length + ack_number