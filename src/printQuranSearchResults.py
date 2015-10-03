
def printResults(ayahs):
	if len(ayahs) > 0:
	    # print ayahs[1]
	    arabicAyah = ayahs[1]["aya"]["text"].encode("utf-8")

	    while arabicAyah.find("<span") > -1:
	        startSpan1 = arabicAyah.find("<span")
	        endSpan1 = arabicAyah.find(">") + 1
	        arabicAyah = arabicAyah[:startSpan1] + arabicAyah[endSpan1:]

	        startSpan2 = arabicAyah.find("</span>")
	        endSpan2 = arabicAyah.find("</span>") + 7
	        arabicAyah = arabicAyah[:startSpan2] + arabicAyah[endSpan2:]

	    print " "
	    print (str(ayahs[1]["sura"]["id"]) + ":" + str(ayahs[1]["aya"]["id"]) + ", " + ayahs[1]["sura"]["english_name"] + " | " + ayahs[1]["sura"]["arabic_name"]).encode("utf-8")
	    print "Og: " + ayahs[1]["aya"]["text"].encode("utf-8")
	    print "Ayah: " + arabicAyah
	    print " "
	else:
	    print "No matches"
	return