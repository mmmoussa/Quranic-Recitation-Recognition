import speech_recognition as sr
import alfanous
import json
import re
import time

from processResults import getMatchItem, mostCommon, printResults


startTime = time.time()
r = sr.Recognizer()
with sr.WavFile("microphone-results-1.wav") as source:
	audio = r.record(source) # read the entire WAV file

try:
	# recognize speech using Google Speech Recognition
	value = r.recognize_google(audio, language = "ar-EG")

	# we need some special handling here to correctly print unicode characters to standard output
	if str is bytes: # this version of Python uses bytes for strings (Python 2)
		print(u"You said {}".format(value).encode("utf-8"))
		ayahs = alfanous.do({"action": "search", "query": value})["search"]["ayas"]
		if len(ayahs) > 0:
			matched = getMatchItem(ayahs[1]) # 1 is number given for top match by alfanous, not list index
			printResults(matched)
		else:
			print "No matches. Trying fuzzy search."
			fuzzyAyahs = alfanous.do({"action": "search", "query": value, "fuzzy": "true"})["search"]["ayas"]
			if len(fuzzyAyahs) > 0:
				matched = getMatchItem(fuzzyAyahs[1]) # 1 is number given for top match by alfanous, not list index
				printResults(matched)
			else:
				print "No matches. Trying spaces."
				spaceAyahs = []
				spaces = [space.start() for space in re.finditer(' ', value)]
				for space in spaces:
					spacedValue = value[:space] + value[(space+1):]
					spacedAyahs = alfanous.do({"action": "search", "query": spacedValue})["search"]["ayas"]
					if len(spacedAyahs) > 0:
						spacedMatched = getMatchItem(spacedAyahs[1])
						spaceAyahs.append(spacedMatched)
				if len(spaceAyahs) > 0:
					mostCommonMatch = mostCommon(value.encode("utf-8"), spaceAyahs)
					printResults(mostCommonMatch)
				else:
					print "No matches. Trying suggestions."
					suggestionAyahs = []
					suggestionsObj = alfanous.do({"action": "suggest", "query": value})["suggest"]
					suggestions = {}
					for a in suggestionsObj:
						suggestions[a] = []
						b = suggestionsObj[a]
						for c in b:
							suggestions[a].append(c)
					
					for i in suggestions:
						for j in suggestions[i]:
							newValue = value.replace(i, j)
							# print i
							# print j
							# print newValue
							newAyahs = alfanous.do({"action": "search", "query": newValue})["search"]["ayas"]
							if len(newAyahs) > 0:
								newMatched = getMatchItem(newAyahs[1])
								suggestionAyahs.append(newMatched)
					if len(suggestionAyahs) > 0:
						mostCommonMatch = mostCommon(value.encode("utf-8"), suggestionAyahs)
						printResults(mostCommonMatch)
					else:
						print "No matches. Trying spaces and suggestions."
						ssAyahs = []
						for i in suggestions:
							for j in suggestions[i]:
								newValue = value.replace(i, j)
								spaces = [space.start() for space in re.finditer(' ', newValue)]
								for space in spaces:
									ssValue = newValue[:space] + newValue[(space+1):]
									newAyahs = alfanous.do({"action": "search", "query": ssValue})["search"]["ayas"]
									if len(newAyahs) > 0:
										ssMatched = getMatchItem(newAyahs[1])
										ssAyahs.append(ssMatched)

						if len(ssAyahs) > 0:
							mostCommonMatch = mostCommon(value.encode("utf-8"), ssAyahs)
							printResults(mostCommonMatch)
							# print suggestionAyahs.count(suggestionAyahs[0])
							# print suggestionAyahs.count(suggestionAyahs[1])
						else:
							print "No matches at all."
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
