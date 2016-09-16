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
        self.last_byte_sent = 0
        self.next_byte_expected = 0
        self.last_byte_acked = 0
        self.last_byte_received = 0
        self.next_ack_expected = 0 
        self.duplicate_acks = 0

    # Do not use for retransmissions
    def send_segment(self, segment):
        sent = pld.send_datagram(self.pld_args[0], self.sock, segment)
        self.sent_segments[segment.sequence] = segment
        self.last_byte_sent = segment.sequence
        if sent:
            print("SENT: {} SEQ: {} ACK: {}, DATA: {}.".format(segment.type, segment.sequence, segment.ack, segment.data))
            # print("LAST BYTE SENT = ", self.last_byte_sent)
            print("--------------------------------------")
            return True
        else:
            self.log.update('drop', segment)
            print("DROPPED PACKET TYPE {}, SEQ: {}, ACK: {}".format(segment.type, segment.sequence, segment.ack))
            # print("LAST BYTE SENT = ", self.last_byte_sent)
            print("--------------------------------------")
            return False

    def receive_segment(self):
        try:
            package, addr = self.sock.recvfrom(self.mss)
            self.segment = Segment.init_from_received(None, self.header_size, package, addr)
            self.log.update('rec', self.segment)
            self.received_segments[self.segment.ack] = self.segment
            print("RECEIVED: {} SEQ: {} ACK: {}, DATA: {}.".format(self.segment.type, self.segment.sequence, self.segment.ack, self.segment.data))
            print("NEXT BYTE EXPECTED = ", self.next_byte_expected)
            print("--------------------------------------")
            return True
        except socket.timeout:
            print("SOCKET HAS TIMED OUT")
            self.reset_window()
            return False

    def correct_receipt(self):
        self.received_segments[self.segment.sequence] = self.segment
        self.last_byte_received = self.segment.sequence

    def establish_send_connection(self):
        self.segment = Segment("S", 0, 0, '', self.to_addr)
        self.send_segment(self.segment)
        self.log.update('snd', self.segment)
        self.receive_segment()
        self.segment = Segment("A", 1, 1, '', self.to_addr)
        self.send_segment(self.segment)
        self.log.update('snd', self.segment)
        self.next_byte_to_send = 1
        self.last_byte_received = 1
        self.next_byte_expected = 1
        self.next_ack_expected = 1
        self.sent_segments.clear()
        self.received_segments.clear()
        print("CONNECTION ESTABLISHED")

    def establish_receive_connection(self):
        self.receive_segment()
        self.to_addr = self.segment.addr
        self.correct_receipt()
        self.segment = Segment("SA", 0, 1, '', self.to_addr)
        self.send_segment(self.segment)
        self.log.update('snd', self.segment)
        self.receive_segment()
        self.correct_receipt()
        self.next_byte_expected = 1
        self.last_byte_sent = 1
        self.sent_segments.clear()
        self.received_segments.clear()
        print("CONNECTION ESTABLISHED")

    def send_ACK(self): 
        self.segment = Segment("A", self.last_byte_sent, self.last_byte_received, '', self.to_addr)
        self.send_segment(self.segment)
        self.last_byte_acked = self.segment.sequence
        return True

    def receive_ACK(self):
        if self.receive_segment():
            print("CHECK: {} == {}".format(self.segment.ack, self.next_ack_expected))
            if self.segment.type == "A" and self.segment.ack == self.next_ack_expected:
                self.correct_receipt()
                self.duplicate_acks = 0
                self.last_byte_acked = self.segment.ack
                print("NEXT ACK EXPECTED = {} + {}".format(self.segment.ack, self.sent_segments[self.segment.ack].data_length))
                self.next_ack_expected = self.segment.ack + self.sent_segments[self.segment.ack].data_length
                return True
            elif self.segment.type == "A" and self.segment.ack == self.last_byte_acked and self.duplicate_acks < 3:
                print("Duplicate ACK, incrementing duplicate counter")
                self.duplicate_acks += 1
                self.log.duplicate_acks += 1
            elif self.segment.type == "A" and self.segment.ack == self.last_byte_acked and self.duplicate_acks >= 3:
                print("THREE DUPLICATE ACKS, RESETTING WINDOW")
                self.log.duplicate_acks += 1
                self.reset_window
            else:
                print("THIS ACK IS NOT IN ANY OF THE CATEGORIES :/")
        else:
            print("DID NOT RECEIVE AN ACK")
            return False

    def retransmit_window(self):
        while self.next_byte_to_send in self.sent_segments:
            retransmission = self.sent_segments[self.next_byte_to_send]
            print("RESENDING:")
            if self.send_segment(retransmission):
                self.log.update('ret', retransmission)
            self.log.packets_retransmitted += 1
            self.next_byte_to_send += len(retransmission.data)
            self.duplicate_acks = 0

    def reset_window(self):
        print("RESETTING THE WINDOW")
        self.last_byte_sent = self.last_byte_acked
        print("UPDATING LAST BYTE SENT TO: ", self.last_byte_sent)
        print("LAST BYTE ACKED: ", self.last_byte_acked)
        self.next_byte_to_send = self.last_byte_acked + self.sent_segments[self.last_byte_acked].data_length
        print("UPDATING NEXT BYTE TO SEND TO: ", self.next_byte_to_send)
        print("NEXT BYTE TO SEND: ", self.next_byte_to_send)
        return True

    def send_data(self):
        print("*******************STARTING THE SEND DATA FUNCTION******************")
        self.sock.settimeout(self.timeout / 1000)
        random.seed(self.pld_args[1])
        f = open(self.filename, "rb")
        data = f.read(self.mss)
        while (data):
            bytes_in_flight = self.last_byte_sent - self.last_byte_acked
            if bytes_in_flight + self.mss <= self.mws: 
                if self.next_byte_to_send in self.sent_segments:
                    self.retransmit_window()
                else:
                    self.segment = Segment("P", self.next_byte_to_send, self.last_byte_received, data, self.to_addr)
                    self.send_segment(self.segment)
                    self.log.data_segments_sent += 1
                    self.next_byte_to_send += self.segment.data_length
                    self.log.bytes_transferred += self.segment.data_length
                    data = f.read(self.mss) 
            else:
                while self.receive_ACK():
                    bytes_in_flight = self.last_byte_sent - self.last_byte_acked
                    continue
        f.close()
        return True

    def receive_data(self):
        print("*********************STARTING THE RECEIVE DATA FUNCTION*******************")
        assembled_file = "" 
        while True:
            self.receive_segment()
            if self.segment.type == "P" and self.segment.ack == self.last_byte_sent and self.segment.sequence == self.next_byte_expected:
                assembled_file += str(self.segment.data, 'ascii')
                print("ADDED: ", self.segment.data)
                print("--------------------------------------")
                self.next_byte_expected += len(self.segment.data)
                # ACK immediately as STP does not support delayed ACKs.
                self.last_byte_received = self.segment.sequence
                self.log.bytes_received += self.segment.data_length
                self.log.data_segments_received += 1
                self.send_ACK()
            elif self.segment.type == "F":
                return assembled_file
            else: 
                self.log.duplicate_segments += 1
                print("IGNORED: ", self.segment.data)
                print("expected ack: {}, received ack: {}".format(self.last_byte_sent, self.segment.ack))
                print("Expected sequence: {}, received sequence: {}".format(self.next_byte_expected, self.segment.sequence))
                segment = Segment("A", 1, self.last_byte_received, '', self.to_addr)
                self.send_segment(segment)

    def teardown_send_connection(self):
        last_segment = self.sent_segments[max(self.sent_segments.keys(), key=int)]
        sequence_number = last_segment.sequence + len(last_segment.data)
        self.segment = Segment("F", sequence_number, self.last_byte_received, '', self.to_addr)
        self.send_segment(self.segment)
        self.log.update('snd', self.segment)
        self.receive_segment()
        if self.segment.type == "FA" and self.segment.ack == self.last_byte_sent:
            self.correct_receipt()
        self.segment = Segment("A", self.segment.ack, self.segment.sequence + 1, '', self.to_addr)
        self.send_segment(self.segment)
        self.log.update('snd', self.segment)
        return True

    def teardown_receive_connection(self, assembled_file):
        if self.segment.type == "F" and self.segment.ack == self.last_byte_sent:
            self.correct_receipt()
        self.last_byte_acked = self.segment.ack
        with open(self.filename, 'w') as f:
            f.write(assembled_file)
            f.close()
        self.segment = Segment("FA", self.last_byte_acked + 1, self.last_byte_received, '', self.to_addr)
        self.send_segment(self.segment)
        self.log.update('snd', self.segment)
        self.next_ack_expected = 3
        self.receive_segment()
        if self.segment.type == "A" and self.segment.ack == self.next_ack_expected:
            self.correct_receipt()
        return True

    def send_file(self, filename):
        self.filename = filename
        self.establish_send_connection()
        self.send_data()
        print("DONE WITH THE SEND DATA CYCLE")
        last_sequence_number = max(self.sent_segments.keys())
        print("LOOPING WHILE {} != {}.".format(self.last_byte_acked, last_sequence_number))
        while self.last_byte_acked != last_sequence_number:
            while self.receive_ACK():
                continue
            if self.last_byte_acked != last_sequence_number:
                self.retransmit_window()
        self.teardown_send_connection()
        self.log.sender_close()
        print("All done, terminating")

    def receive_file(self, filename):
        self.filename = filename
        self.establish_receive_connection()
        assembled_file = self.receive_data()
        self.teardown_receive_connection(assembled_file)
        self.log.receiver_close()
        print("All done, terminating")
