import json
import io

with io.open("quran.json", 'r', encoding='utf8') as quran:
	quranObj = json.load(quran)

uniqueAyahList = []
uniqueAyahObjects = []

for surahNum, surah in enumerate(quranObj):
	for ayahNum, ayah in enumerate(surah["arabic"]):
		if ayah not in uniqueAyahList:
			uniqueAyahList.append(ayah)
			uniqueAyahObjects.append({"text": ayah, "ids": [[surahNum + 1, ayahNum + 1]]})
		else:
			for obj in uniqueAyahObjects:
				if obj["text"] == ayah:
					obj["ids"].append([surahNum + 1, ayahNum + 1])

largestRepeatAmount = 0
mostRepeatedAyahObj = {}

for i in uniqueAyahObjects:
	currentLength = len(i["ids"])
	if currentLength > largestRepeatAmount:
		largestRepeatAmount = currentLength
		mostRepeatedAyahObj = i

print largestRepeatAmount

with io.open('QuranRepeats.json', 'w', encoding='utf8') as json_file:
    data = json.dumps(uniqueAyahObjects, indent=4, ensure_ascii=False)
    # unicode(data) auto-decodes data to unicode if str
    json_file.write(unicode(data))

repeatList = []

for i in uniqueAyahObjects:
	currentLength = len(i["ids"])
	if currentLength > 1:
		repeatList.append(i["ids"])

print repeatList
