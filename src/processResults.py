# -*- coding: utf-8 -*-

from Levenshtein import ratio
import alfanous
import re
import io
import json


def processText(value, skip=False):
	# * and ? have special meaning in alfanous, and so need to be removed
	value = value.replace("*", "")
	value = value.replace("?", "")
	ayahs = alfanous.do({"action": "search", "query": value})["search"]["ayas"]
	if len(ayahs) > 0 and not skip:
		specialCasesResult = specialCases(value)
		if specialCasesResult:
			print "Matched a special case."
			return specialCasesResult
		levList = []
		for item in ayahs:
			if item < 4: # Only use best 3 alfanous results
				matched = getMatchItem(ayahs[item])
				levList.append(matched)
		bestMatch = bestLevMatch(value.encode("utf-8"), levList)
		if bestMatch is not None:
			printResults(bestMatch)
			return responseJSON(value, bestMatch)
		else:
			return processText(value, skip=True) # Restart call ignoring initial results
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
			return responseJSON(value, mostCommonMatch)
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
				return responseJSON(value, mostCommonMatch)
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
					return responseJSON(value, mostCommonMatch)
				else:
					print "No matches at all."
					return responseJSON(value, {}, empty=True)

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
		# Remove html highlighting provided by alfanous from the ayah
		startSpan1 = arabicAyah.find("<span")
		endSpan1 = arabicAyah.find(">") + 1
		arabicAyah = arabicAyah[:startSpan1] + arabicAyah[endSpan1:]

		startSpan2 = arabicAyah.find("</span>")
		endSpan2 = arabicAyah.find("</span>") + 7
		arabicAyah = arabicAyah[:startSpan2] + arabicAyah[endSpan2:]

	matchItem["surahNum"] = ayah["sura"]["id"]
	matchItem["ayahNum"] = ayah["aya"]["id"]
	matchItem["englishSurahName"] = ayah["sura"]["english_name"]
	matchItem["arabicSurahName"] = ayah["sura"]["arabic_name"].encode("utf-8")
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
		print (str(ayah["surahNum"]) + ":" + str(ayah["ayahNum"]) + ", " + ayah["englishSurahName"] + " | " + ayah["arabicSurahName"].decode("utf-8"))
		print "Ayah: " + ayah["arabicAyah"]
		print " "

def specialCases(value):
	# if success return responseJSON
	# else
	return False

	# TODO: Handle special cases such as surahs with letters and
	# not words (eg. 2:1)

	# Idea for doing this: Keep a list made up of lists with two items.
	# The first item is the way Google hears the speacial ayah and the 
	# second item is the correct match object to return. If a query 
	# matches the first item, call responseJSON with the two items.


def responseJSON(initialValue, match, empty=False, multipleMatches=False):	
	with io.open("quran.json", 'r', encoding='utf8') as quran:
		quranObj = json.load(quran)

	if match:
		match["englishAyah"] = quranObj[match["surahNum"] - 1]["english"][match["ayahNum"] - 1]

	returnObj = {
		"queryText": initialValue.encode('utf-8'),
		"match": match,
		"empty": empty,
		"multipleMatches": multipleMatches,
		"otherMatches": [],
	}



	return returnObj

	# TODO: Handle repeated ayahs

	# Idea for doing this: Maintain lists of matching verses, 
	# using their surah number and ayah number as references 
	# and also storing the english and arabic surah name. Once
	# the responseJSON function is triggered, check if the match
	# is in any of the lists. If it is, add each item in the
	# list except the original match to otherMatches, using the
	# details stored in the list as well as the arabic ayah text
	# from the match item.

	# Useful resource: http://www.mobware4u.com/blog/quran-repeated-verses

