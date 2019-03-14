#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
import sys
import asyncio
import random

async def doubler_server(host = '127.0.0.1', port = 8080):
	server = await asyncio.start_server(
		handle_connection, host, port)
	addr = server.sockets[0].getsockname()
	async with server:
		await server.serve_forever()

async def handle_connection(reader, writer):
	data = 'dummy'
	addr = writer.get_extra_info('peername')
	print('Connected by', addr)
	while True:
		data = await reader.read(100)
		if not data:
			break
		res = int(data.decode())*2
		writer.write(f"{res}".encode())
		await writer.drain()
	print('Disconnected by', addr)
	writer.close()

async def doubler_client(host = '127.0.0.1', port = 8080):
	reader, writer = await asyncio.open_connection(
		host, port)
	while True:
		n = random.randrange(10)
		writer.write(f"{n}\n".encode())
		data = await reader.read(100)
		print(n, data.decode())
		await asyncio.sleep(random.random()*2)

if __name__ == '__main__':
	if sys.argv[1] == 'server':
		asyncio.run(doubler_server())
	else:
		assert sys.argv[1] == 'client'
		asyncio.run(doubler_client())