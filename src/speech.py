import speech_recognition as sr
import alfanous
import json

from processResults import getMatchItem, printResults


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
                    print "No matches"
                    suggestionsObj = alfanous.do({"action": "suggest", "query": value})["suggest"]
                    suggestions = {}
                    for a in suggestionsObj:
                        suggestions[a] = []
                        b = suggestionsObj[a]
                        for c in b:
                            suggestions[a].append(c)
                    
                    for i in suggestions:
                        for j in suggestions[i]:
                            value = value.replace(i, j)
                            # print i
                            # print j
                            print value
                            sAyahs = alfanous.do({"action": "search", "query": value})["search"]["ayas"]
                            sMatched = printResults(sAyahs)



            else: # this version of Python uses unicode for strings (Python 3+)
                print("You said {}".format(value))
        except sr.UnknownValueError:
            print("Sorry, unable to understand recitation.")
        except sr.RequestError:
            print("Sorry, couldn't request results from Google Speech Recognition service")
except KeyboardInterrupt:
    pass
