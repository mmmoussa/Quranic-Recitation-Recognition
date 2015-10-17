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

	print(u"You said {}".format(value).encode("utf-8"))
	processText(value)
	elapsedTime = time.time() - startTime
	print "Elapsed time: " + str(elapsedTime)
except sr.UnknownValueError:
	print("Oops! Didn't catch that")
except sr.RequestError:
	print("Uh oh! Couldn't request results from Google Speech Recognition service")
except KeyboardInterrupt:
	pass
