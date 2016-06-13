from time import sleep
from twinkle import TwinkleLights

lights = TwinkleLights(["192.168.1.1", "192.168.1.2"]);

while True:
	lights.set_color((0xFF, 0x00, 0x00), 0xFF)
	sleep(5)
	for index in xrange(0,13):
		lights.set_color_triplet((0x00, 0x00, 0xFF), 0xFF, index)
		sleep(1)

	lights.set_off()
	sleep(1)
