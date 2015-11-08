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

	with io.open("surahNames.json", 'r', encoding='utf8') as surahNames:
		surahNamesObj = json.load(surahNames)

	matchItem["surahNum"] = ayah["sura"]["id"]
	matchItem["ayahNum"] = ayah["aya"]["id"]
	matchItem["englishSurahName"] = surahNamesObj[0]["english"][ayah["sura"]["id"] - 1]
	matchItem["arabicSurahName"] = surahNamesObj[0]["arabic"][ayah["sura"]["id"] - 1].encode("utf-8")
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


def responseJSON(initialValue, match, empty=False):	
	multipleMatches = False
	otherMatches = []

	if match:
		with io.open("quran.json", 'r', encoding='utf8') as quran:
			quranObj = json.load(quran)

		match["englishAyah"] = quranObj[match["surahNum"] - 1]["english"][match["ayahNum"] - 1]

		repeatingVerseList = [
			[[2, 1], [3, 1], [29, 1], [30, 1], [31, 1], [32, 1]],
			[[2, 5], [31, 5]], 
			[[2, 47], [2, 122]], 
			[[2, 134], [2, 141]], 
			[[3, 89], [24, 5]], [[3, 182], [8, 51]], 
			[[5, 10], [5, 86]], 
			[[6, 4], [36, 46]], 
			[[6, 10], [21, 41]], 
			[[6, 15], [39, 13]], 
			[[7, 78], [7, 91]], 
			[[7, 107], [26, 32]], 
			[[7, 108], [26, 33]], 
			[[7, 121], [26, 47]], 
			[[7, 122], [26, 48]], 
			[[7, 183], [68, 45]], 
			[[9, 33], [61, 9]], 
			[[9, 73], [66, 9]], 
			[[10, 48], [21, 38], [27, 71], [34, 29], [36, 48], [67, 25]], 
			[[11, 96], [40, 23]], 
			[[14, 20], [35, 17]], 
			[[15, 5], [23, 43]], 
			[[15, 29], [38, 72]], 
			[[15, 30], [38, 73]], 
			[[15, 34], [38, 77]], 
			[[15, 36], [38, 79]], 
			[[15, 37], [38, 80]], 
			[[15, 38], [38, 81]], 
			[[15, 40], [38, 83]], 
			[[15, 45], [51, 15]], 
			[[15, 58], [51, 32]], 
			[[16, 42], [29, 59]], 
			[[17, 48], [25, 9]], 
			[[18, 89], [18, 92]], 
			[[20, 24], [79, 17]], 
			[[23, 5], [70, 29]], 
			[[23, 6], [70, 30]], 
			[[23, 7], [70, 31]], 
			[[23, 8], [70, 32]], 
			[[23, 26], [23, 39]], 
			[[26, 1], [28, 1]], 
			[[26, 2], [28, 2]], 
			[[26, 8], [26, 67], [26, 103], [26, 121], [26, 174], [26, 190]], 
			[[26, 9], [26, 68], [26, 104], [26, 122], [26, 140], [26, 159], [26, 175], [26, 191]], 
			[[26, 66], [37, 82]], 
			[[26, 107], [26, 125], [26, 143], [26, 162], [26, 178]], 
			[[26, 108], [26, 110], [26, 126], [26, 131], [26, 144], [26, 150], [26, 163], [26, 179]], 
			[[26, 109], [26, 127], [26, 145], [26, 164], [26, 180]], 
			[[26, 147], [44, 52]], 
			[[26, 153], [26, 185]], 
			[[26, 171], [37, 135]], 
			[[26, 172], [37, 136]], 
			[[26, 173], [27, 58]], 
			[[26, 204], [37, 176]], 
			[[27, 3], [31, 4]], 
			[[28, 62], [28, 74]], 
			[[37, 17], [56, 48]], 
			[[37, 27], [52, 25]], 
			[[37, 40], [37, 74], [37, 128], [37, 160]], 
			[[37, 43], [56, 12]], 
			[[37, 78], [37, 108], [37, 129]], 
			[[37, 80], [37, 121], [37, 131], [77, 44]], 
			[[37, 81], [37, 111], [37, 132]], 
			[[37, 154], [68, 36]], 
			[[38, 87], [81, 27]], 
			[[40, 1], [41, 1], [42, 1], [43, 1], [44, 1], [45, 1], [46, 1]], 
			[[43, 2], [44, 2]], 
			[[43, 83], [70, 42]], 
			[[45, 2], [46, 2]], 
			[[52, 19], [77, 43]], 
			[[52, 40], [68, 46]], 
			[[52, 41], [68, 47]], 
			[[54, 16], [54, 21], [54, 30]], 
			[[54, 17], [54, 22], [54, 32], [54, 40]], 
			[[55, 13], [55, 16], [55, 18], [55, 21], [55, 23], [55, 25], [55, 28], [55, 30], [55, 32], [55, 34], [55, 36], [55, 38], [55, 40], [55, 42], [55, 45], [55, 47], [55, 49], [55, 51], [55, 53], [55, 55], [55, 57], [55, 59], [55, 61], [55, 63], [55, 65], [55, 67], [55, 69], [55, 71], [55, 73], [55, 75], [55, 77]], 
			[[56, 13], [56, 39]], 
			[[56, 67], [68, 27]], 
			[[56, 74], [56, 96], [69, 52]], 
			[[56, 80], [69, 43]], 
			[[59, 1], [61, 1]], 
			[[68, 15], [83, 13]], 
			[[69, 21], [101, 7]], 
			[[69, 22], [88, 10]], 
			[[69, 34], [107, 3]], 
			[[69, 40], [81, 19]], 
			[[73, 19], [76, 29]], 
			[[74, 55], [80, 12]], 
			[[77, 15], [77, 19], [77, 24], [77, 28], [77, 34], [77, 37], [77, 40], [77, 45], [77, 47], [77, 49], [83, 10]], 
			[[79, 33], [80, 32]], 
			[[82, 13], [83, 22]], 
			[[83, 9], [83, 20]], 
			[[83, 23], [83, 35]], 
			[[84, 2], [84, 5]], 
			[[109, 3], [109, 5]]
		]

		matchList = []
		chechSurahNum = match["surahNum"]
		checkAyahNum = match["ayahNum"]

		for group in repeatingVerseList:
			for item in group:
				if item[0] == chechSurahNum and item[1] == checkAyahNum:
					matchList = group
					multipleMatches = True

		if multipleMatches:
			with io.open("surahNames.json", 'r', encoding='utf8') as surahNames:
				surahNamesObj = json.load(surahNames)

			for item in matchList:
				otherMatches.append({
					"surahNum": item[0],
					"ayahNum": item[1],
					"englishSurahName": surahNamesObj[0]["english"][item[0] - 1],
					"arabicSurahName": surahNamesObj[0]["arabic"][item[0] - 1],
					"englishAyah": quranObj[item[0] - 1]["english"][item[1] - 1],
					"arabicAyah": quranObj[item[0] - 1]["arabic"][item[1] - 1],
				})

	returnObj = {
		"queryText": initialValue.encode('utf-8'),
		"match": match,
		"empty": empty,
		"multipleMatches": multipleMatches,
		"otherMatches": otherMatches,
	}

	return returnObj

