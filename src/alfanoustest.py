# -*- coding: utf-8 -*-

import alfanous

from printQuranSearchResults import printResults


value = u"و التين و الزيتون"

ayahs = alfanous.do({"action":"search", "query":value, "fuzzy": "True"})["search"]["ayas"]
printResults(ayahs)

