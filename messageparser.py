import os, io, re, time
import pymorphy2
import helpers
from collections import Counter

morph = pymorphy2.MorphAnalyzer()

replaceRules = {'ии':['и']}

_startTime = time.time()

class MessageParser: #splits message into words and feeds a wordparser
    def __init__(self, wordParser):
        self.wordParser = wordParser
        self.pattern = re.compile('[\W_]+')

    def feed(self, message):
        message = self.pattern.sub(' ', message)
        words = message.split(' ')
        if words is None:
            words = [message]

        clearWords = []
        for word in words:
            word = word.strip()
            if len(word) <= 0:
                continue
            if word in replaceRules:
                clearWords.extend(replaceRules[word])
            else:
                clearWords.append(word)

        for word in clearWords:
            self.wordParser.feed(word)

    def finalize(self):
        self.wordParser.finalize()
        self.wordParser.saveData()
        
class WordCounter:
    def __init__(self):
        self.wordsCounter = Counter()
        self.frequentWordsCounter = Counter()
        self.unknownWordsCounter = Counter()
        
    def feed(self, word):
        if word in self.wordsCounter:
            self.wordsCounter[word] += 1
        else:
            p = morph.parse(word)
            if 'UNKN' in p[0].tag:
                self.unknownWordsCounter[p[0].normal_form] += 1
            self.wordsCounter[p[0].normal_form] += 1

    def finalize(self):
        frequencyTable = Counter()
        
        print("Reading from: " + helpers._wordFrequencyLemmsLoc)
        f = io.open(helpers._wordFrequencyLemmsLoc, 'r', encoding="UTF-8")
        for text in f:
            lemma = text.split(' ')
            frequencyTable[lemma[2]] = float(lemma[1])
        f.close()

        for word in self.wordsCounter.most_common():
            frequency = max(frequencyTable[word[0]], 1)
            self.frequentWordsCounter[word[0]] = word[1] * 100000 / frequency
        
    def saveData(self):
        print("Writing to: " + helpers._wordsDataLoc)
        f = io.open(helpers._wordsDataLoc, 'w+', encoding="UTF-8")
        for word in wordparser.wordsCounter.most_common():
            f.write(str(word[1]) + ":" + word[0] + "\n")
        f.close()

        print("Writing to: " + helpers._unknownWordsDataLoc)
        f = io.open(helpers._unknownWordsDataLoc, 'w+', encoding="UTF-8")
        for word in wordparser.unknownWordsCounter.most_common():
            f.write(str(word[1]) + ":" + word[0] + "\n")
        f.close()

        print("Writing to: " + helpers._frequentWordsDataLoc)
        f = io.open(helpers._frequentWordsDataLoc, 'w+', encoding="UTF-8")
        for word in wordparser.frequentWordsCounter.most_common():
            f.write(str(word[1]) + ":" + word[0] + "\n")
        f.close()
                
        
def parseMessages():
    if not os.path.exists(helpers._messagesDataLoc):
        print(helpers._messagesDataLoc + " is not exists!")
        return

    wordparser = WordCounter()
    messageParser = MessageParser(wordparser)
    parsedLines = 0

    print("Reading from: " + helpers._messagesDataLoc)
    f = io.open(helpers._messagesDataLoc, 'r', encoding="UTF-8")
    for text in f:
        messageParser.feed(text)
        parsedLines += 1
        if parsedLines % 100 == 0:
            print("Parsed " + str(parsedLines) + " lines")
    f.close()

    messageParser.finalize()

    print("Completed in " + helpers.timeSince(_startTime) + "!")
