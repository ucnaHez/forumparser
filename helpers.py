# -*- coding: UTF-8 -*-
import time, io

rawDataLoc =               "rawData"
rawTopicsDataLoc =         rawDataLoc + "/topics"
rawUserpagesDataLoc =      rawDataLoc + "/users"

processedDataLoc =         "processedData"
messagesDataLoc =          processedDataLoc + "/messages"
quotesDataLoc =            processedDataLoc + "/quotes"
allMessagesDataLoc =       processedDataLoc + "/allMessages.txt"
allQuotesDataLoc =         processedDataLoc + "/allQuotes.txt"
allUserdataDataLoc =       processedDataLoc + "/allUserdata.txt"
wordsDataLoc =             processedDataLoc + "/words.txt"
unknownWordsDataLoc =      processedDataLoc + "/unknownWords.txt"
frequentWordsDataLoc =     processedDataLoc + "/frequentWords.txt"
citationCountDataLoc =     processedDataLoc + "/citationCount.txt"
ratedContentDataLoc =      processedDataLoc + "/ratedContent.txt"
topicStartersDataLoc =     processedDataLoc + "/topicStarters.txt"
msgsCountDataLoc =         processedDataLoc + "/publicMessagesCount.txt"
userRepDataLoc =           processedDataLoc + "/userRep.txt"
repEfficencyDataLoc =      processedDataLoc + "/repEfficency.txt"

wordFrequencyRuLoc =   "__lemma2.txt"
wordFrequencyEnLoc =   "__lemma3.txt"
cookiesDataLoc = "__private_key.txt"

threadCount = 2
topicCount = 18891
usersCount = 7931 # :3
startFrom = 1

errorText = "Извините, мы не можем найти это!"
notExistsText = """<p class='ipsType_sectiontitle'>
			Эта страница не существует
		</p>"""
noAccessText = """<p class='ipsType_sectiontitle'>
			Вы не можете просматривать эту тему.
		</p>"""
userNotExists = """Вы запросили профиль несуществующего пользователя."""
userNotAvailable = """Этот пользователь больше не активен."""
nginxError = "Sorry, the page you are looking for is currently unavailable."
discordTitle = "Discord - Free voice and text chat for gamers"
onyxDiscordTitle = "Check out the Chaotic Onyx community on Discord"

cookies = {}

def isDiscord(dat):
    return discordTitle in dat or onyxDiscordTitle in dat

def isErrorPage(dat):
    return errorText in dat or nginxError in dat or userNotExists in dat or userNotAvailable in dat

def isPageNotExists(dat):
    return notExistsText in dat

def isNoAccessToPage(dat):
    return noAccessText in dat

def timeSince(startTime):
    return time.strftime("%M:%S", time.gmtime(time.time() - startTime))

def loadPrivateKey():
    f = io.open(cookiesDataLoc, 'r', encoding="UTF-8")
    for text in f:
        if text.startswith('#'):
            continue
        text = text.strip().split(' ')
        cookies[text[0].strip()] = text[1].strip()
    f.close()

def getPageURL(topicID, page = None, entry = None):
    if entry is None:
        if page is None:
            return 'http://forum.ss13.ru/index.php?showtopic={0}'.format(topicID)
        else:
            return 'http://forum.ss13.ru/index.php?showtopic={0}&st={1}'.format(topicID, (int(page) - 1) * 20)
    else:
        if page is None:
            return 'http://forum.ss13.ru/index.php?showtopic={0}#entry={2}'.format(topicID, entry)
        else:
            return 'http://forum.ss13.ru/index.php?showtopic={0}&st={1}#entry{2}'.format(topicID, (int(page) - 1) * 20, entry)

def getUserpageURL(userID):
    return 'http://forum.ss13.ru/index.php?showuser={0}'.format(userID)

def getPageFilename(topicID, page):
    return '{0:06d}.{1:06d}.html'.format(topicID, page)

def getUserpageFilename(userID):
    return '{0:06d}.html'.format(userID)
