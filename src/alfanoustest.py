# -*- coding: utf-8 -*-

import alfanous

from processResults import getMatchItem, printResults


value = u"و التين و الزيتون"

suggestions = alfanous.do({"action": "suggest", "query": value})["suggest"]

for i in suggestions:
	print i.encode("utf-8")
	a = suggestions[i]
	for j in a:
		print j.encode("utf-8")
	print " "
# printResults(ayahs)

