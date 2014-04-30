#!/usr/bin/env python
import os
import sys
import socket
import random
import argparse
import select
import threading

import signal

signal.signal(signal.SIGINT, lambda x, y: sys.exit(1))

BUF_SIZE = 4096
BIND_HOST = '0.0.0.0'

def usage(p):
    p.print_help()
    sys.exit(1)

def tmux_socket():
    tmux = os.getenv('TMUX')
    if not tmux: raise Exception("Not running tmux")
    return tmux.split(',')[0]

def proxy_data(sockets):
    while True:
        r, w, e = select.select(sockets, [], [], 0)
        for sock in r:
            other = filter(lambda x: x != sock, sockets)[0]
            data = sock.recv(BUF_SIZE)
            if not data:
                sys.exit(0)
            other.sendall(data)

def listen():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tmux = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    tmux.connect(tmux_socket())
    for i in range(100): # Plenty of attempts
        port = random.randint(32767, 65535)
        try:
            listener.bind((BIND_HOST, port))
            break
        except socket.error:
            continue
    else:
        raise Exception("Couldn't find a port to bind to ")
    print("Bound to %s:%d" % (BIND_HOST, port))

    listener.listen(1)
    (client, addr) = listener.accept()

    proxy_data((client, tmux))

def connect(hostspec):
    host, port = hostspec.split(":")
    port = int(port)

    remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    # Skeeeetchy
    local_socket_name = os.tempnam()
    local.bind(local_socket_name)

    remote.connect((host, port))

    local.listen(1)
    # print
    # Preeetty much the reason we can't have nice things
    threading.Thread(target=lambda: os.system("TMUX=%s tmux new" % (local_socket_name))).run()
    (conn, addr) = local.accept()

    proxy_data((conn, remote))

def _get_parser():
    p = argparse.ArgumentParser()
    p.add_argument("--listen", dest='listen', action="store_true")
    p.add_argument("--connect", dest='connect', action="store")
    return p

if __name__ == '__main__':
    parser = _get_parser()
    args = parser.parse_args()
    if (args.listen and args.connect):
        usage(parser)

    if args.listen:
        listen()
    elif args.connect:
        connect(args.connect)
    else:
        usage()
