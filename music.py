import time
from datetime import datetime
from twinkle import TwinkleLights
import os
import thread

#Extension for audio files.
MUSIC_EXTENSION = ".m4a"

#The hour to start the light show. 24 hour time.
START_HOUR = 17
#The hour to stop the light show. 24 hour time.
STOP_HOUR = 23
#Command to play an audio file. The afplay command is for OS X.
MUSIC_COMMAND = "afplay \"{0}\""

#Just for paranoia if offsets don't match the music length.
#Dont want music playing over other music.
KILL_MUSIC_COMMAND = "killall afplay"

#Temp file to store audio onsets. Could be done without a temp file, but this
#was easy and convenient for debugging.
ONSET_FILE = "onsets.txt"
AUBIO_COMMAND = "aubioonset \"{0}\" -O hfc > " + ONSET_FILE


#On OS X when playing through bluetooth it takes around 1/2 a second for the
#audio to start. Playing direct has no real perceptible delay.
AUDIO_DELAY = 0.5

#Control two sets of lights. More sets should be able to be added. It doesn't
#hurt to include strings that don't exist.
lights = TwinkleLights(["192.168.1.1", "192.168.1.2"]);

#Lost of colors. Red, Green, and White.
COLORS = [(0xFF, 0x00, 0x00), (0x00, 0xFF, 0x00), (0xFF, 0xFF, 0xFF)]
INTENSITY = 0xFF

playlist = []

lights_on = True

def should_play():
	current_hour = datetime.time(datetime.now()).hour
	return (current_hour >= START_HOUR) and (current_hour < STOP_HOUR)

def generate_onsets(song):
	onsets = []
	os.system(AUBIO_COMMAND.format(song))

	with open(ONSET_FILE) as onset_file:
		for onset in onset_file:
			onset_time = float(onset)
			onsets.append(onset_time)

	return onsets

#Find files in the current directory with the right extension.
for file in os.listdir("./"):
	if file.endswith(MUSIC_EXTENSION):
		playlist.append(file)
		print file

while True:
	#Wait around until it is time to play.
	if not should_play():
		if lights_on:
			lights.set_off()
			lights_on = False
		time.sleep(10)
		continue

	for song in playlist:
		#If it is time to turn off do not play the next song.
		if not should_play():
			break

		lights_on = True
		onsets = generate_onsets(song)

		start_time = time.clock()

		color_index = 0

		thread.start_new_thread(os.system, (MUSIC_COMMAND.format(song),))

		for onset_time in onsets:
			if color_index >= len(COLORS):
				color_index = 0

			can_play = False

			#Using a busy loop makes the changes more accurate than sleeping.
			#If someone was concerned about power they could sleep.
			while not can_play:
					elapsed_time = time.clock() - start_time
					if elapsed_time >= (onset_time + AUDIO_DELAY):
						can_play = True

			lights.set_color(COLORS[color_index], INTENSITY)
			color_index = color_index + 1

		os.system(KILL_MUSIC_COMMAND)


