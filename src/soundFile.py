import speech_recognition as sr
import time

from processResults import *


startTime = time.time()
r = sr.Recognizer()
with sr.WavFile("microphone-results.wav") as source:
	audio = r.record(source) # read the entire WAV file

try:
	# recognize speech using Google Speech Recognition
	value = r.recognize_google(audio, language = "ar-EG")

	# we need some special handling here to correctly print unicode characters to standard output
	if str is bytes: # this version of Python uses bytes for strings (Python 2)
		print(u"You said {}".format(value).encode("utf-8"))
		processText(value)
		elapsedTime = time.time() - startTime
		print "Elapsed time: " + str(elapsedTime)
	else: # this version of Python uses unicode for strings (Python 3+)
		print("You said {}".format(value))
except sr.UnknownValueError:
	print("Oops! Didn't catch that")
except sr.RequestError:
	print("Uh oh! Couldn't request results from Google Speech Recognition service")
except KeyboardInterrupt:
	pass
