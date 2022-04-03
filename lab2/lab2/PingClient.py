#!/usr/bin/python3
#coding: utf-8
"""
COMP9331 Lab2
Andrew Lau z3330164

Usage:
    python3 PingClient.py [HOST] [PORT]

Note that I have used the below template as a starting point:
https://webcms3.cse.unsw.edu.au/COMP3331/22T1/resources/70208
"""
from socket import *
from datetime import datetime
import time
import sys

# allow command line arguments, otherwise take defaults
if len(sys.argv) == 3:
    SERVER_NAME = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])
else:
    SERVER_NAME = '127.0.0.1'  # equivalent to 'localhost'
    SERVER_PORT = 2000  #change this port number if required

SEQUENCE_NUMBER_START = 3331
MAX_MESSAGES = 15

# This line creates the client’s socket. The first parameter indicates the
# address family; in particular,AF_INET indicates that the underlying network 
# is using IPv4.The second parameter indicates that the socket is of type 
# SOCK_DGRAM,which means it is a UDP socket (rather than a TCP socket, where we 
# use SOCK_STREAM).
client_socket = socket(AF_INET, SOCK_DGRAM)
# setting timeout to 600ms
client_socket.settimeout(0.6)

# list of RTTs for reporting at the end
rtt_list = []

# send MAX_MESSAGES number of messages
for message_no in range(MAX_MESSAGES):
    message = f'PING {SEQUENCE_NUMBER_START + message_no} {datetime.now().strftime("%H:%M:%S")}\r\n'

    time_start = time.time()  # record when we went the message
    # Now that we have a socket and a message, we will want to send the message 
    # through the socket to the destination host.
    client_socket.sendto(message.encode(),(SERVER_NAME, SERVER_PORT))
    # Note the difference between UDP sendto() and TCP send() calls. In TCP we do 
    # not need to attach the destination address to the packet, while in UDP we 
    # explicilty specify the destination address + Port No for each message

    # try to listen for a message
    try:
        modifiedMessage, serverAddress = client_socket.recvfrom(SERVER_PORT)
        # Note the difference between UDP recvfrom() and TCP recv() calls.
        # print message from server
        # print(modifiedMessage.decode())
        # print the received message
        # calculate RTT and convert to milliseconds
        rtt = round((time.time() - time_start) * 1000)
        rtt_list.append(rtt)
    except timeout:  # timeout, packet loss
        rtt = 'time out'

    print(f'ping to {SERVER_NAME}, seq = {message_no + 1}, rtt = {rtt}')

client_socket.close()
# Close the socket

# report summary statistics of RTT
print('*' * 80)
print(f'Attempted to send {MAX_MESSAGES} messages to {SERVER_NAME} on port {SERVER_PORT}')
print(f'Of the {len(rtt_list)} successful packets received:')
print(f'\tthe minimum RTT was {min(rtt_list)}ms')
print(f'\tthe maximum RTT was {max(rtt_list)}ms')
print(f'\tthe average RTT was {round(sum(rtt_list) / len(rtt_list))}ms')
