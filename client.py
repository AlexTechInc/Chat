import tkinter 
import socket
import threading
import sys
import time

DEFAULT_USERNAME = "client"

MAX_MESSAGE_LENGTH = 256
MAX_USERNAME_LENGTH = 16

PACKET_SIZE = MAX_USERNAME_LENGTH + MAX_MESSAGE_LENGTH + 6 + 2;

HOST = "localhost"

to_bytes = lambda n: n.to_bytes(1, "big")

if (len(sys.argv) == 2): 
	DEFAULT_USERNAME = sys.argv[1][:MAX_USERNAME_LENGTH]
	print("username set to -> ", DEFAULT_USERNAME)

class main:
	def __init__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# try:
		# 	self.sock.bind((HOST, 7890))
		# except socket.error as error:
		# 	print("An error occured -> ", error.errno)
		# 	sys.exit(1)

		try:
			print("Connecting...")
			self.sock.connect((HOST, 7890))
		except socket.error as error:
			if (error.errno == 10061):
				print("Server is offline!")
			else:
				print("An error occured -> ", error.errno)
			
			sys.exit(1)

		self.sock.setblocking(False)
		# self.sock.listen()

		self.running = True

		# self.connections = []
		self.lastFrom = ""

		# self.acceptThread = threading.Thread(target=self.accept)
		# self.acceptThread.start()

		self.receiverThread = threading.Thread(target=self.receiver)
		self.receiverThread.start()
			
		self.win()

	def generatePacket(self, message, username=DEFAULT_USERNAME):
		packet = b"$%_"  # magic bytes

		packet += to_bytes(len(username))
		packet += username.encode("utf8")

		packet += to_bytes(len(message))
		packet += message.encode("utf8")

		packet += b"_%$"  # magic bytes

		return packet
	def decodePacket(self, packet): 
		if (packet[:3] == b"$%_" and packet[-3:] == b"_%$"):
			packet = packet[3: -3]

			username = packet[1: packet[0] + 1].decode()
			message = packet[packet[0] + 2: ].decode()

			return [username, message]

		else: return

	def appendMessage(self, message, username=DEFAULT_USERNAME):
		self.inputField.delete(0, 'end')
		if username and message:
			print(f"inserted -> {username}: {message}")

			self.messagesField.insert(tkinter.END, ("\n" * (bool(self.lastFrom) and self.lastFrom != username)) + f"{username}: {message}" + "\n")
			self.lastFrom = username

	# def send(self, message, username=DEFAULT_USERNAME):
	# 	self.appendMessage(message, username)

	# 	if self.connections:
	# 		for pair in self.connections:
	# 			try:
	# 				size = pair[0].send(self.generatePacket(message, username))
	# 				print(f"sent { size } to -> {pair[1][0]}:{pair[1][1]}")

	# 			except Exception as e:
	# 				print("And error occured -> ", e)

	# 	else: print("no connections")

	# 	return

	def send(self, message, username=DEFAULT_USERNAME):
		self.appendMessage(message, username)

		try:
			self.sock.send(self.generatePacket(message, username))

		except socket.error as error:
			if (error.errno == 10053):
				self.appendMessage("Server closed the connection.", "#service")
				# print("Server closed the connection. Bye")
				# self.destroy()

			# print("And error occured -> ", e)

		# if self.connections:
		# 	for pair in self.connections:
		# 		try:
		# 			size = pair[0].send(self.generatePacket(message, username))
		# 			print(f"sent { size } to -> {pair[1][0]}:{pair[1][1]}")

		# 		except Exception as e:
		# 			print("And error occured -> ", e)

		# else: print("no connections")

		# return

	# def close(self):

	def destroy(self):
		self.running = False
		print("destroy")

		self.root.destroy()

		sys.exit(0)

	def win(self):
		self.root = tkinter.Tk()
		self.root.geometry("360x480")
		self.root.title("CHAT | " + DEFAULT_USERNAME)
		self.root.resizable(False, False)


		self.root.protocol("WM_DELETE_WINDOW", self.destroy)
		
		self.messagesField = tkinter.Text(self.root, height=33, font=("Lucida Console", 10))
		self.inputField = tkinter.Entry(self.root, font=("Lucida Console", 11))
		self.sendButton = tkinter.Button(self.root, text=">", font=("Lucida Console", 20), height=20, width=2, command=lambda: self.send(self.inputField.get()[: MAX_MESSAGE_LENGTH]))

		self.messagesField.bind("<Key>", lambda e: "break")

		self.inputField.bind("<Return>", lambda e: self.send(self.inputField.get()))

		self.messagesField.pack()
		self.inputField.pack(ipady=8, pady=5, padx=5, ipadx=60, side="left")
		self.sendButton.pack(pady=5, side="left")

		self.root.mainloop()

	# Threads 
	# def accept(self):
	# 	print("accept started")

	# 	while self.running:
	# 		try:	
	# 			pair = self.sock.accept()
	# 			pair[0].setblocking(False)
	# 			self.connections.append(pair)
	# 			print(f"new connnection -> {pair[1][0]}:{pair[1][1]}")
	# 		except socket.error as error:
	# 			if error.errno != 10035:
	# 				print("An error occured -> ", error.errno)
	# 				self.sock.close()
	# 				sys.exit(1)

	# 	return

	# def receiver(self):
	# 	print("receiver started")

	# 	while (self.running):
	# 		if (self.connections):
	# 			for pair in self.connections:
	# 				try:
	# 					packet = self.decodePacket(pair[0].recv(PACKET_SIZE))

	# 					if (packet):
	# 						self.appendMessage(packet[1], username=packet[0])
	# 				except:
	# 					pass
		
	# 	return

	def receiver(self):
		print("receiver started")

		while (self.running):
			try:
				data = self.sock.recv(PACKET_SIZE)

				if (not data):
					break

				packet = self.decodePacket(data)

				if (packet):
					self.appendMessage(packet[1], username=packet[0])
			
			except socket.error as error:
				if (error.errno != 10035):
					print("An error occured -> ", error.errno)
					self.destroy()
					sys.exit(1)

		print("Server closed the connection.")
		self.appendMessage("Server closed the connection.", "#service")
		
		return		

main()