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


def send_datagram(pdrop, sock, stp_package, address):
    roll = random.random();

    # print("luck = {}, roll = {}.".format(1-pdrop, roll))

    if (roll <= (1-pdrop)):
        sock.sendto(stp_package, address)
        print("packet was SUCCESSFULLY TRANSMITTED")
        return True
    else:
        print("packet was DROPPED")
        return False
