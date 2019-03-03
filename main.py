#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

import socket
import sys
import random
import time
from threading import Thread
import selectors

def doubler_server(port = 8080):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.bind(('', port))
		s.listen(5)
		s.setblocking(False)
		sel = selectors.DefaultSelector()
		sel.register(s, selectors.EVENT_READ)
		while True:
			for key, mask in sel.select():
				if key.fileobj is s:
					conn, addr = s.accept()
					print('Connected by', addr)
					conn.setblocking(False)
					sel.register(conn, selectors.EVENT_READ)
				else:
					conn = key.fileobj
					data = conn.recv(1024)
					if not data:
						conn.close()
						print('Disconnected by', addr)
						sel.unregister(conn)
						continue
					n = int(data.decode())
					res = f"{n*2}\n".encode()
					conn.send(res)

def doubler_client(port = 8080):
	with socket.create_connection(("127.0.0.1", port)) as s:
		f = s.makefile(mode="rw", buffering=1, newline="\n")
		while True:
			n = random.randrange(10)
			f.write(f"{n}\n")
			print(n, f.readline().strip())
			time.sleep(random.random()*2)

if __name__ == '__main__':
	if sys.argv[1] == 'server':
		doubler_server()
	else:
		assert sys.argv[1] == 'client'
		doubler_client()