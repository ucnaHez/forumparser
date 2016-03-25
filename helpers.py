import time

_rawDataLoc =           "rawData"
_processedDataLoc =     "processedData"

_wordFrequencyLemmsLoc = "__lemma.txt"

_messagesDataLoc =      _processedDataLoc + "\\messages.txt"
_wordsDataLoc =         _processedDataLoc + "\\words.txt"
_unknownWordsDataLoc =  _processedDataLoc + "\\unknownWords.txt"
_frequentWordsDataLoc = _processedDataLoc + "\\frequentWords.txt"

_threadCount = 1
_topicCount = 2

_errorText = "Извините, мы не можем найти это!"
_notExistsText = """<p class='ipsType_sectiontitle'>
			Эта страница не существует
		</p>"""
_noAccessText = """<p class='ipsType_sectiontitle'>
			Вы не можете просматривать эту тему.
		</p>"""

def isErrorPage(dat):
    return _errorText in dat

def isPageNotExists(dat):
    return _notExistsText in dat

def isNoAccessToPage(dat):
    return _noAccessText in dat

def timeSince(startTime):
    return time.strftime("%M:%S", time.gmtime(time.time() - startTime))
