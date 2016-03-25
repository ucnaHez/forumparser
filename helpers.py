import time, io

_rawDataLoc =           "rawData"
_processedDataLoc =     "processedData"

_wordFrequencyLemmsLoc = "__lemma2.txt"

_messagesDataLoc =      _processedDataLoc + "\\messages.txt"
_quotesDataLoc =        _processedDataLoc + "\\quotes.txt"
_wordsDataLoc =         _processedDataLoc + "\\words.txt"
_unknownWordsDataLoc =  _processedDataLoc + "\\unknownWords.txt"
_frequentWordsDataLoc = _processedDataLoc + "\\frequentWords.txt"
_citationCountDataLoc = _processedDataLoc + "\\citationCount.txt"

_cookiesDataLoc = "__private_key.txt"

_threadCount = 3
_topicCount = 15000

_errorText = "Извините, мы не можем найти это!"
_notExistsText = """<p class='ipsType_sectiontitle'>
			Эта страница не существует
		</p>"""
_noAccessText = """<p class='ipsType_sectiontitle'>
			Вы не можете просматривать эту тему.
		</p>"""
_nginxError = "Sorry, the page you are looking for is currently unavailable."

_cookies = {}

def isErrorPage(dat):
    return _errorText in dat or _nginxError in dat

def isPageNotExists(dat):
    return _notExistsText in dat

def isNoAccessToPage(dat):
    return _noAccessText in dat

def timeSince(startTime):
    return time.strftime("%M:%S", time.gmtime(time.time() - startTime))

def loadPrivateKey():
    f = io.open(_cookiesDataLoc, 'r', encoding="UTF-8")
    for text in f:
        if text.startswith('#'):
            continue
        text = text.strip().split(' ')
        _cookies[text[0].strip()] = text[1].strip()
    f.close()
