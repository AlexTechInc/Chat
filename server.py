import tkinter 
import socket
import threading
import sys

DEFAULT_USERNAME = "server"

MAX_MESSAGE_LENGTH = 256
MAX_USERNAME_LENGTH = 16

PACKET_SIZE = MAX_USERNAME_LENGTH + MAX_MESSAGE_LENGTH + 6 + 2;

HOST = "0.0.0.0"

to_bytes = lambda n: n.to_bytes(1, "big")

class main:
	def __init__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.sock.bind((HOST, 7890))
		except socket.error as error:
			print("An error occured -> ", error.errno)
			sys.exit(1)

		self.sock.setblocking(False)
		self.sock.listen()

		self.running = True

		self.connections = []
		self.lastFrom = ""

		self.acceptThread = threading.Thread(target=self.accept)
		self.acceptThread.start()

		self.receiverThread = threading.Thread(target=self.receiver)
		self.receiverThread.start()

		if (not ("--no-window" in sys.argv)): 
			self.win()
		
		else:
			self.runningMessage()

	def runningMessage(self):
		print("   _____                   _             ")
		print("  |  __ \\                 (_)            ")
		print("  | |__) |   _ _ __  _ __  _ _ __   __ _ ")
		print("  |  _  / | | | '_ \\| '_ \\| | '_ \\ / _` |")
		print("  | | \\ \\ |_| | | | | | | | | | | | (_| |")
		print("  |_|  \\_\\__,_|_| |_|_| |_|_|_| |_|\\__, |")
		print("                                    __/ |")
		print("                                   |___/ \n")

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

	def send(self, message, username=DEFAULT_USERNAME, cast=None):
		if not cast:
			self.appendMessage(message, username)

		if self.connections:
			for pair in self.connections:
				try:
					if (pair[0] != cast):
						size = pair[0].send(self.generatePacket(message, username))
						print(f"sent { size } to -> {pair[1][0]}:{pair[1][1]}")

				except Exception as e:
					print("And error occured -> ", e)

		else: print("no connections")

		return

	def win(self):
		self.root = tkinter.Tk()
		self.root.geometry("360x480")
		self.root.title("CHAT | " + DEFAULT_USERNAME)
		self.root.resizable(False, False)

		def destroy():
			self.running = False
			print("destroy")
			# self.winThread.join()
			self.root.destroy()

		self.root.protocol("WM_DELETE_WINDOW", destroy)
		
		self.messagesField = tkinter.Text(self.root, height=33, font=("Lucida Console", 10))
		self.inputField = tkinter.Entry(self.root, font=("Lucida Console", 11))
		self.sendButton = tkinter.Button(self.root, text=">", font=("Lucida Console", 20), height=20, width=2, command=lambda: self.send(self.inputField.get()[: MAX_MESSAGE_LENGTH], username="$" + DEFAULT_USERNAME))

		self.messagesField.bind("<Key>", lambda e: "break")

		self.inputField.bind("<Return>", lambda e: self.send(self.inputField.get(), username="$" + DEFAULT_USERNAME))

		self.messagesField.pack()
		self.inputField.pack(ipady=8, pady=5, padx=5, ipadx=60, side="left")
		self.sendButton.pack(pady=5, side="left")

		self.root.mainloop()

	# Threads 
	def accept(self):
		print("accept started")

		while self.running:
			try:	
				pair = self.sock.accept()
				pair[0].setblocking(False)
				self.connections.append(pair)
				print(f"new connnection -> {pair[1][0]}:{pair[1][1]}")
			except socket.error as error:
				if error.errno != 10035:
					print("An error occured -> ", error.errno)
					self.sock.close()
					sys.exit(1)

		return
	def receiver(self):
		print("receiver started")

		while (self.running):
			if (self.connections):
				for pair in self.connections:
					try:
						packet = self.decodePacket(pair[0].recv(PACKET_SIZE))

						if (packet):
							self.appendMessage(packet[1], username=packet[0])

							self.send(packet[1], username=packet[0], cast=pair[0])
					except socket.error as error:
						if (error.errno != 10035): 
							print("And error occured in receiver -> ", error.errno)
		
		return			

main()