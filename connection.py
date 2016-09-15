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
import socket
import random
import pld
from log import Log
from segment import Segment                         # helper



class Connection:

    def __init__(self, sock, log_filename, addr=(), receiver=None, mws=17520, 
                mss=1460, timeout=99999, pld_args=(0,0)):
        self.header_size = 9                        # bytes
        self.sock = sock
        self.start = time.clock()
        self.log = Log(log_filename, self.start)
        self.to_addr = receiver                     # 2-tuple: (IP, port)
        self.filename = None
        self.mws = int(mws)
        self.mss = int(mss)
        self.timeout = float(timeout)
        self.pld_args = pld_args

        self.sent_segments = {}
        self.received_segments = {}
        self.last_byte_sent = 0                     # Sender
        self.last_byte_acked = 0                    # Sender
        self.last_byte_received = 0                 # Receiver
        self.segment = None

    # Do not use for retransmissions
    def send_segment(self, segment):
        sent = pld.send_datagram(self.pld_args[0], self.sock, segment)
        self.sent_segments[segment.sequence] = segment
        self.last_byte_sent = segment.sequence
        if sent:
            self.log.update('snd', segment)
            print("SENT: {} SEQ: {} ACK: {}".format(segment.type, segment.sequence, segment.ack))
            print("--------------------------------------")
            return True
        else:
            self.log.update('drop', segment)
            print("DROPPED THIS PACKET")
            print("--------------------------------------")
            return False

    def receive_segment(self):
        while True:
            try:
                package, addr = self.sock.recvfrom(self.mss)
                self.segment = Segment.init_from_received(None, self.header_size, package, addr)
                self.log.update('rec', self.segment)
                print("RECEIVED: {}, SEQ:{}, ACK: {}".format(self.segment.type, self.segment.sequence, self.segment.ack))
                return True
            except socket.timeout:
                return False

    def correct_receipt(self):
        self.received_segments[self.segment.sequence] = self.segment
        self.last_byte_received = self.segment.sequence
        print("CORRECT")
        print("--------------------------------------")

    def send_SYN(self):
        self.segment = Segment("S", 0, 0, '', self.to_addr)
        self.send_segment(self.segment)

    def receive_SYN(self):
        self.receive_segment()
        if self.segment.type == "S":
            self.to_addr = self.segment.addr
            self.correct_receipt()
            return True
        else:
            receive_SYN()

    def send_SYNACK(self):
        self.segment = Segment("SA", 0, self.last_byte_acked + 1, '', self.to_addr)
        self.send_segment(self.segment)
        self.last_byte_sent += 1

    def receive_SYNACK(self):
        self.receive_segment()
        if self.segment.type == "SA" and self.segment.ack == self.last_byte_sent + 1:
            self.correct_receipt()
            return True
        else:
            self.receive_SYNACK()

    def send_ACK(self, seq_increment, ack_increment): 
        self.segment = Segment("A", self.last_byte_sent + seq_increment, self.last_byte_received + ack_increment, '', self.to_addr)
        self.send_segment(self.segment)
        self.last_byte_acked = self.segment.sequence
        return True

    def receive_ACK(self, increment):
        if self.receive_segment():
            print("CHECK: {} >= {}".format(self.segment.ack,self.last_byte_acked + increment))
            if self.segment.type == "A" and self.segment.ack >= self.last_byte_acked + increment:
                self.correct_receipt()
                self.last_byte_acked = self.segment.ack + increment
                return True
            elif self.segment.type == "FA":
                return True
            else:
                print("ACK WAS INCORRECT")

    def send_data(self):
        self.sock.settimeout(self.timeout / 1000)
        random.seed(self.pld_args[1])
        
        self.last_byte_received += 1
        current_sequence = self.last_byte_sent + 1
        
        f = open(self.filename, "rb")
        data = f.read(self.mss)
        while (data):
            bytes_in_flight = (self.last_byte_sent - self.last_byte_acked)
            if bytes_in_flight + self.mss <= self.mws: 
                print('current_sequence = ', current_sequence)
                if current_sequence in self.sent_segments:
                    retransmission = self.sent_segments[current_sequence]
                    self.send_segment(retransmission)
                    print("RESENT SEQ: {} DATA: {}".format(retransmission.sequence, retransmission.data))
                    self.log.packets_retransmitted += 1
                    current_sequence += len(retransmission.data)
                else:                    
                    self.segment = Segment("P", current_sequence, self.last_byte_received, data, self.to_addr)
                    print("SENT SEQ: {} DATA: {}".format(self.segment.sequence, data))
                    self.send_segment(self.segment)
                    data = f.read(self.mss)
                    current_sequence += len(self.segment.data)
            elif bytes_in_flight + self.mss > self.mws and self.receive_ACK(0):
                self.receive_ACK(0)
            else:
                print("Looks like we timed out - we need to retransmit")
                last_received_segment = self.sent_segments[self.last_byte_acked]
                current_sequence = last_received_segment.sequence + len(last_received_segment.data)
                self.last_byte_sent = current_sequence
                print("CURRENT SEQUENCE: ", current_sequence)
        f.close()
        return True

    def receive_data(self):
        assembled_file = "" 
        expected_sequence = self.last_byte_received + 1
        while True:
            self.receive_segment()
            if self.segment.type == "P" and self.segment.ack == self.last_byte_sent and self.segment.sequence == expected_sequence:
                assembled_file += str(self.segment.data, 'ascii')
                print("ADDED: ", self.segment.data)
                print("--------------------------------------")
                expected_sequence += len(self.segment.data)
                # ACK immediately as STP does not support delayed ACKs.
                self.last_byte_received = self.segment.sequence
                self.send_ACK(0, 0)
            elif self.segment.type == "F" and self.segment.ack == self.last_byte_sent:
                self.receive_FIN(assembled_file)
                return True
            else: 
                print("IGNORED: ", self.segment.data)
                print("expected ack: {}, received ack: {}".format(self.last_byte_sent, self.segment.ack))
                print("Expected sequence: {}, received sequence: {}".format(expected_sequence, self.segment.sequence))

    def send_FIN(self):
        last_segment = self.sent_segments[max(self.sent_segments.keys(), key=int)]
        sequence_number = last_segment.sequence + len(last_segment.data)
        self.segment = Segment("F", sequence_number, self.last_byte_received, '', self.to_addr)
        self.send_segment(self.segment)
        return last_segment

    def receive_FIN(self, assembled_file):
        self.correct_receipt()
        self.last_byte_acked = self.segment.ack
        with open(self.filename, 'w') as f:
            f.write(assembled_file)
            f.close()

    def send_FINACK(self):
        self.segment = Segment("FA", self.last_byte_acked + 1, self.last_byte_received + 1, '', self.to_addr)
        self.send_segment(self.segment)
        return True

    def receive_FINACK(self):
        # self.receive_segment()
        if self.segment.type == "FA" and self.segment.ack == self.last_byte_sent + 1:
            self.correct_receipt()
            return True
        else:
            print("INCORRECT FINACK")

    def send_file(self, filename):
        self.filename = filename
        self.send_SYN()
        self.receive_SYNACK()
        self.send_ACK(1, 1)
        self.send_data()
        last_segment = self.send_FIN()
        while self.segment.ack != last_segment.sequence + len(last_segment.data) + 1:
            self.receive_ACK(0)
        self.receive_FINACK()
        self.send_ACK(1, 0)
        self.log.close()
        print("All done, terminating")

    def receive_file(self, filename):
        self.filename = filename
        self.state = 'LISTEN'
        self.receive_SYN()
        self.send_SYNACK()
        self.receive_ACK(0)
        self.receive_data()
        self.send_FINACK()
        self.receive_ACK(1)
        self.log.close()
        print("All done, terminating")
