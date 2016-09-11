# This class module contains all of the basic functions required for Simple
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
import time
from stp_segment import Segment                         # helper
import pld
import random


class Connection:
    header_size = 9 # bytes

    def __init__(self, sock, log_filename, addr=(), receiver=(), MWS=None, 
                MSS=None, timeout=None, pld_args=None):
        self.sock = sock
        self.log_filename = log_filename
        self.segment = None
        self.prev_segment = None
        self.addr = addr                               # 2-tuple: (IP, port)
        self.receiver_addr = receiver                  # 2-tuple: (IP, port)
        self.send_filename = None
        self.output_filename = None
        self.MWS = MWS
        self.timeout = timeout
        self.sequence_number = 0                        # Temp => change to random no. after testing
        self.ack_number = 0                        # Temp => change to random no. after testing
        self.start = time.clock()
        self.pld_args = pld_args

        l = vars(self)
        print(l)

    def receive_segment(self):
        while True:
            data, addr = self.sock.recvfrom(48 + self.header_size)
            header = data[:self.header_size+1]
            data = data[self.header_size:]
            segment_type, sequence_number, ack_number = self.interpret_header(header)
            self.segment = Segment(segment_type, sequence_number, ack_number, data, addr)
            self.update_log('rec')
            print("Received TYPE: {}, SEQ:{}, ACK: {}".format(self.segment.type, self.segment.sequence, self.segment.ack))
            self.ack_number = self.segment.sequence
            print("NEW ACK NUMBER:", self.segment.sequence)
            return

    def interpret_header(self, header):
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

    def send_SYN(self):
        ack_number = 0
        self.segment = Segment("SYN", self.sequence_number, ack_number, '')
        print("Sending SYN to:", self.receiver_addr)
        self.sock.sendto(self.segment.package, self.receiver_addr)
        segment_time = self.update_log('snd')
        self.sequence_number += 1

    def receive_SYN(self):
        self.receive_segment()
        if self.segment.type == "SYN":
            self.receiver_addr = self.segment.addr[0]
            return 
        else:
            receive_SYN()

    def send_SYNACK(self):
        self.segment = Segment("SYNACK", self.sequence_number, self.segment.sequence + 1, '')
        self.sock.sendto(self.segment.package, self.receiver_addr)
        segment_send_time = self.update_log('snd')

    def receive_SYNACK(self):
        self.receive_segment()
        print("expected_ack = {}, received_ack_no= {}".format(self.sequence_number, self.segment.ack))
        if self.segment.type == "SYNACK" and self.segment.ack == self.sequence_number:
            return
        else:
            self.receive_SYNACK()

    def send_ACK(self, increment): 
        self.segment = Segment("ACK", self.sequence_number, self.segment.sequence + increment, '')
        self.sock.sendto(self.segment.package, self.receiver_addr)
        self.update_log('snd')
        return

    def receive_ACK(self, increment):
        self.receive_segment()
        print("expected_ack= {}, received_ack_no= {}".format(self.sequence_number + increment, self.segment.ack))
        if self.segment.type == "ACK" and self.segment.ack == self.sequence_number + increment:
            return
        else:
            self.receive_ACK(increment)

    def send_data(self, filename):
        f = open(filename, "rb")
        data = f.read(48)
        random.seed(self.pld_args[1])
        while (data):
            self.segment = Segment("PUSH", self.segment.ack + len(data), self.segment.sequence, data)
            if (pld.send_datagram(float(self.pld_args[0]), self.sock, self.segment.package, self.receiver_addr)):
                self.update_log('snd')
                print("Sent PUSH. SEQ {}, ACK: {}, DATA:".format(self.segment.sequence, self.segment.ack, self.segment.data))
                self.sequence_number += len(data)
                self.receive_ACK(0)
                data = f.read(48)
            else:
                print("YEAH IT DIDN'T MAKE IT")
                break
            print("--------------------------------------")
        f.close()

    def receive_data(self, filename):
        self.sequence_number += 1
        assembled_file = "" 
        while True:
            self.receive_segment()
            print("expected_ack= {}, received_ack_no= {}".format(self.sequence_number, self.segment.ack))
            if self.segment.type == "PUSH" and self.segment.ack == self.sequence_number:
                assembled_file += self.segment.data
                print("ADDED: ", self.segment.data)
                self.send_ACK(0)
                print("Sent ACK. SEQ {}, ACK: {}".format(self.segment.sequence, self.segment.ack))
            elif self.segment.type == "FIN" and self.segment.ack == self.sequence_number:
                with open(filename, 'w') as f:
                    f.write(assembled_file)
                    f.close()
                return 
            print("--------------------------------------")

    def send_FIN(self):
        self.sequence_number += 1
        self.segment = Segment("FIN", self.sequence_number, self.ack_number, '')
        self.sock.sendto(self.segment.package, self.receiver_addr)
        self.update_log('snd')
        return 

    def receive_FIN(self):
        self.receive_segment()
        print("expected_ack= {}, received_ack_no= {}".format(self.sequence_number + 1, self.segment.ack))
        if self.segment.type == "FIN" and self.segment.ack == self.sequence_number + 1:
            self.sequence_number += 1
            return
        else:
            self.receive_FIN()

    def send_file(self, filename):
        self.send_SYN()
        self.receive_SYNACK()
        print("Sent {} SEQ: {} ACK: {}".format(self.segment.type, self.segment.sequence, self.segment.ack))
        self.send_ACK(1)
        print("Sent {} SEQ: {} ACK: {}".format(self.segment.type, self.segment.sequence, self.segment.ack))
        self.send_data(filename)
        self.send_FIN()
        print("Sent {} SEQ: {} ACK: {}".format(self.segment.type, self.segment.sequence, self.segment.ack))
        self.receive_ACK(1)
        self.receive_FIN()
        self.send_ACK(1)
        print("Sent {} SEQ: {} ACK: {}".format(self.segment.type, self.segment.sequence, self.segment.ack))
        print("Received final FIN and sent final ACK, TERMINATING")

    def receive_file(self, filename):
        self.receive_SYN()
        self.send_SYNACK()
        print("Sent: {} SEQ: {} ACK: {}".format(self.segment.type, self.segment.sequence, self.segment.ack))
        self.receive_ACK(1)
        self.receive_data(filename)
        self.send_ACK(1)
        self.ack_number += 1
        print("Sent: {} SEQ: {} ACK: {}".format(self.segment.type, self.segment.sequence, self.segment.ack))
        self.send_FIN()
        print("Sent: {} SEQ: {} ACK: {}".format(self.segment.type, self.segment.sequence, self.segment.ack))
        self.receive_ACK(1)
        print("All done, terminating")

    def update_log(self, entry_type):
        log_time, segment_time = self.time_since_start()
        log_entry = '{:6}'.format(entry_type) + log_time + self.segment.log + '\n'
        with open(self.log_filename, 'a') as f:
            f.write(log_entry)
            f.close()
        return segment_time

    def time_since_start(self):
        segment_time = time.clock() - self.start
        return '{:6}'.format(str(round((segment_time) * 1000, 2))), segment_time