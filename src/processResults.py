# -*- coding: utf-8 -*-

from Levenshtein import ratio
import alfanous
import re


def processText(value, skip=False):
	ayahs = alfanous.do({"action": "search", "query": value})["search"]["ayas"]
	if len(ayahs) > 0 and not skip:
		specialCases(value)
		levList = []
		for item in ayahs:
			if item < 4:
				matched = getMatchItem(ayahs[item])
				levList.append(matched)
		bestMatch = bestLevMatch(value.encode("utf-8"), levList)
		if bestMatch is not None:
			printResults(bestMatch)
		else:
			processText(value, skip=True)
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
					else:
						print "No matches at all."

def getMatchItem(ayah):
	matchItem = {
		"surahNum": 0,
		"ayahNum": 0,
		"englishSurahName": "",
		"arabicSurahName": "",
		"arabicAyah": "",
	}
	
	arabicAyah = ayah["aya"]["text"].encode("utf-8")

	while arabicAyah.find("<span") > -1:
		startSpan1 = arabicAyah.find("<span")
		endSpan1 = arabicAyah.find(">") + 1
		arabicAyah = arabicAyah[:startSpan1] + arabicAyah[endSpan1:]

		startSpan2 = arabicAyah.find("</span>")
		endSpan2 = arabicAyah.find("</span>") + 7
		arabicAyah = arabicAyah[:startSpan2] + arabicAyah[endSpan2:]

	matchItem["surahNum"] = ayah["sura"]["id"]
	matchItem["ayahNum"] = ayah["aya"]["id"]
	matchItem["englishSurahName"] = ayah["sura"]["english_name"]
	matchItem["arabicSurahName"] = ayah["sura"]["arabic_name"]
	matchItem["arabicAyah"] = arabicAyah

	return matchItem

def mostCommon(spoken, lst):
	highestCountItem = max(lst, key=lst.count)
	highestCount = lst.count(highestCountItem)
	contenders = []
	for item in lst:
		if (lst.count(item) == highestCount) and (item not in contenders):
			contenders.append(item)
	if len(contenders) > 1:
		# print contenders
		print "\nContending"
		bestMatch = ["None", 0]
		for ayah in contenders:
			score = ratio(spoken, ayah["arabicAyah"])
			print ayah["arabicAyah"]
			print score
			if score > bestMatch[1]:
				bestMatch = [ayah, score]
		return bestMatch[0]
	else:
		return highestCountItem

def bestLevMatch(spoken, lst):
	print " "
	bestMatch = ["None", 0]
	for ayah in lst:
		score = ratio(spoken, ayah["arabicAyah"])
		print ayah["arabicAyah"]
		print score
		if score > bestMatch[1]:
			bestMatch = [ayah, score]
	if bestMatch[1] > 0.5:
		return bestMatch[0]
	else:
		return None

def printResults(ayah):
		print " "
		print (str(ayah["surahNum"]) + ":" + str(ayah["ayahNum"]) + ", " + ayah["englishSurahName"] + " | " + ayah["arabicSurahName"]).encode("utf-8")
		print "Ayah: " + ayah["arabicAyah"]
		print " "

def specialCases(value):
	pass

