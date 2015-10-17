import speech_recognition as sr
import time

from processResults import *


r = sr.Recognizer()
m = sr.Microphone(sample_rate=44100)
m.CHUNK = 8192

try:
	print("Beginning session...")
	with m as source:
		r.adjust_for_ambient_noise(source)
		# print("Set minimum energy threshold to {}".format(r.energy_threshold))
		print("Please begin recitation...")
		audio = r.listen(source)
		print("Got it! Now to recognize it...")

		# write audio to a WAV file
		with open("microphone-results.wav", "wb") as f:
			f.write(audio.get_wav_data())

		try:
			startTime = time.time()
			# recognize speech using Google Speech Recognition
			value = r.recognize_google(audio, language = "ar-EG")

			print(u"You said {}".format(value).encode("utf-8"))
			processText(value)
			elapsedTime = time.time() - startTime
			print "Elapsed time: " + str(elapsedTime)
		except sr.UnknownValueError:
			print("Sorry, unable to understand recitation.")
		except sr.RequestError:
			print("Sorry, couldn't request results from Google Speech Recognition service")
except KeyboardInterrupt:
	pass
