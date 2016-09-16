#!/usr/bin/python3 -u
#
# This module implements Packet Loss and Delay (PLD) for Simple Transport
# Protocol (STP). Upon receiving an STP segment, this module will drop
# the datagram with a probability of 'pdrop', and forward the datagram with
# a probability of (1 - pdrop). 
# 
# Written by Juliana Zhu, z3252163 
# Written for COMP9331 16s2, Assignment 1. 
#
# Python 3.0


import random
from segment import Segment

def send_datagram(pdrop, sock, segment):
    pdrop = float(pdrop)
    # All non-PUSH packets bypass this segment.
    if segment.type == "P":
        roll = random.random();
        if segment.type == "P" and (roll <= (1-pdrop)):
            sock.sendto(segment.package, segment.addr)
            return True
        else:
            return False
    else:
        sock.sendto(segment.package, segment.addr)
        return True