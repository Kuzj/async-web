#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

import socket
import sys
import random
import time
import types
from threading import Thread
from enum import Enum
from queue import Queue, Empty

class Op(Enum):
	RECV = 1
	SEND = 2
	WAIT = 3

def doubler_server(port = 8080):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.bind(('', port))
		s.listen(5)
		s.setblocking(False)
		q = Queue()
		while True:
			try:
				conn, addr = s.accept()
			except BlockingIOError:
				#continue
				time.sleep(0.1)
				#print('queue size', q.qsize())
				for _ in range(q.qsize()):
					h = q.get()
					try:
						op, arg = h.send(None)
						#print(op, arg)
						#op, arg = h.send(None)
					except StopIteration:
						break
					q.put(h)
				continue
			conn.setblocking(False)
			print('Connection by', addr)
			q.put(handle_connection(conn, addr))

@types.coroutine
def for_recv(conn):
	data = conn.recv(1024)
	yield Op.RECV, data
	return data

@types.coroutine
def for_wait():
	yield Op.WAIT, None

@types.coroutine
def for_send(conn, res):
	yield Op.SEND, conn.send(res) 

async def handle_connection(conn, addr):
	while True:
		try:
			data = await for_recv(conn)
		except BlockingIOError:
			await for_wait()
			continue
		print(addr, 'data', data)
		if not data:
			conn.close()
			print('Disconnected by', addr)
			break
		n = int(data.decode())
		res = f"{n*2}\n".encode()
		#print(res)
		await for_send(conn, res)

def doubler_client(port = 8080, delay = 1):
	with socket.create_connection(("127.0.0.1", port)) as s:
		f = s.makefile(mode="rw", buffering=1, newline="\n")
		while True:
			n = random.randrange(10)
			f.write(f"{n}\n")
			print(n, f.readline().strip())
			#time.sleep(random.random()*2)
			time.sleep(delay)

if __name__ == '__main__':
	if sys.argv[1] == 'server':
		doubler_server()
	else:
		assert sys.argv[1] == 'client'
		doubler_client(delay = int(sys.argv[2]))