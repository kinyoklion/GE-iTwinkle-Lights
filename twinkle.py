#Basic module for controlling the GE iTwinkle WiFi lights.
import socket
import time
import os

class TwinkleLights:
	UDP_PORT = 1281

	#All of the commands to the device are prefixed with this string.
	BASE_CMD = "kleCMD"

	#The password needs to be appended to each string. The ASCII values have 10
	#subtracted. The default password is "2015" which are ASCII values 50, 48, 49,
	#and 53. Subtract 10 from each and you get "(&'+". If you change the password
	#you will need to change this.
	PASSWORD = "(&'+"

	#Commands. There are other commands, but these are the fun ones. The others are
	#just for using the pre-programmed sequences.

	#Set the color of the entire string.
	SETCOLOR = "18"

	#Set the color for 3 of the bulbs on the string. This is non-destructive to the
	#lights not included in the commant.
	SETTHREECOLOR = "05"

	#Number of times to send each command. The commands are not 100% reliable.
	REDUNDANCY = 2

	def __init__(self, light_ips):
		"""Construct an instance of the TwinkleLights with a list of IP addresses."""
		#List of light IP addresses to control. They seem to be sequentially 
		#assinged so the second string should be 192.168.1.2. Add more IP
		#addresses to control more strings. The lights will synchronize by
		#default with only sending commands to the first string, but the other
		#strings will be delayed. Sending to all strings mostly eliminates
		#this. There are some synchronization issues sometimes.
		self._light_ips = light_ips
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		#Timing will be a little more accurate overall if the socket doesn't block.
		self._sock.setblocking(0)


	def set_color(self, color, intensity):
		"""Set the string of lights to the specified color. The color should be
		in the format (RR,GG,BB) with each channel being 0x00-0xFF. So
		(0xFF, 0x00, 0x00) would indicate full red. The intensity is a single
		value from 0x00-0xFF."""
		command = self.BASE_CMD + self.SETCOLOR + "%02x"%intensity + \
			self._convert_color(color) + self.PASSWORD

		self._send_command(command)

			

	def set_color_triplet(self, color, intensity, light_group):
		"""Set the string of lights to the specified color. The color should be
		in the format (RR,GG,BB) with each channel being 0x00-0xFF. So
		(0xFF, 0x00, 0x00) would indicate full red. The intensity is a single
		value from 0x00-0xFF. The light_group should be a single number from
		0-12 with 0 being the first three lights and 1 being the second and so
		on."""
		command = self.BASE_CMD + self.SETTHREECOLOR + "%02x"%light_group + \
			self._convert_color(color) + self.PASSWORD

		self._send_command(command)

	def set_off(self):
		"""Turn off the lights."""
		self.set_color((0, 0, 0), 0)

	def _convert_color(self, color_tuple):
		"""Convert an RGB color to a BGR hex color string."""
		return "".join(["%02x"%c for c in reversed(color_tuple)])

	def _send_command(self, command):
		for ip in self._light_ips:
			for attempt in xrange(self.REDUNDANCY):
				self._sock.sendto(command, (ip, self.UDP_PORT))



