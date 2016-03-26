import os, io, re, time
import pymorphy2
import helpers
from collections import Counter

morph = pymorphy2.MorphAnalyzer()

replaceRules = {'ии':'и'}
        
class WordCounter:
    def __init__(self):
        self.name = "Frequent words counter"
        self.pattern = re.compile('[\W_]+')
        self.wordsCounter = Counter()
        self.frequentWordsCounter = Counter()
        self.unknownWordsCounter = Counter()

    def doWork(self):
        print("Reading from: " + helpers._messagesDataLoc)
        f = io.open(helpers._messagesDataLoc, 'r', encoding='UTF-8')
        for text in f:
            msg = text.split('||')
            words = self.pattern.sub(' ', msg[4]).split()
            if words is None:
                words = [msg[4]]
        
            clearWords = []
            for word in words:
                word = word.strip()
                if len(word) <= 1:
                    continue
                if word in replaceRules:
                    clearWords.append(replaceRules[word])
                else:
                    clearWords.append(word)

            for word in clearWords:
                if word in self.wordsCounter:
                    self.wordsCounter[word] += 1
                else:
                    p = morph.parse(word)
                    # S:
                    n = p[0].normal_form.replace('ё', 'е')
                    if 'UNKN' in p[0].tag:
                        self.unknownWordsCounter[n] += 1
                    self.wordsCounter[n] += 1
        f.close()
            
    def finalize(self):
        frequencyTable = Counter()
        
        print("Reading from: " + helpers._wordFrequencyLemmsLoc)
        f = io.open(helpers._wordFrequencyLemmsLoc, 'r', encoding="UTF-8")
        for text in f:
            lemma = text.strip().split(' ')
            frequencyTable[lemma[1]] = float(lemma[0])
        f.close()
        
        for word in self.wordsCounter.most_common():
            frequency = max(frequencyTable[word[0]], 1)
            self.frequentWordsCounter[word[0]] = round(word[1] * 100000 / frequency)
        
    def saveData(self):
        print("Writing to: " + helpers._wordsDataLoc)
        f = io.open(helpers._wordsDataLoc, 'w+', encoding="UTF-8")
        for word in self.wordsCounter.most_common():
            f.write(str(word[1]) + ":" + word[0] + "\n")
        f.close()

        print("Writing to: " + helpers._unknownWordsDataLoc)
        f = io.open(helpers._unknownWordsDataLoc, 'w+', encoding="UTF-8")
        for word in self.unknownWordsCounter.most_common():
            f.write(str(word[1]) + ":" + word[0] + "\n")
        f.close()

        print("Writing to: " + helpers._frequentWordsDataLoc)
        f = io.open(helpers._frequentWordsDataLoc, 'w+', encoding="UTF-8")
        for word in self.frequentWordsCounter.most_common():
            f.write(str(word[1]) + ":" + word[0] + "\n")
        f.close()

class CitationCounter:
    def __init__(self):
        self.name = "Most citated content"
        self.nicknameCounter = Counter()

    def doWork(self):
        print("Reading from: " + helpers._quotesDataLoc)
        f = io.open(helpers._quotesDataLoc, 'r', encoding="UTF-8")
        for text in f:
            msg = text.split('||')
            self.nicknameCounter[msg[0]] += 1
        f.close()

    def finalize(self):
        return

    def saveData(self):
        print("Writing to: " + helpers._citationCountDataLoc)
        f = io.open(helpers._citationCountDataLoc, 'w+', encoding="UTF-8")
        for word in self.nicknameCounter.most_common():
            f.write(str(word[1]) + ":" + word[0] + "\n")
        f.close()

class MostLeastVotedContent:
    def __init__(self):
        self.name = "Most and least voted content"
        self.mostVoted = []
        self.leastVoted = []
        

        for i in range(10):
            self.mostVoted.append((1, "No sender", "No ID"))
            self.leastVoted.append((-1, "No sender", "No ID"))
        
    def doWork(self):
        print("Reading from: " + helpers._messagesDataLoc)
        f = io.open(helpers._messagesDataLoc, 'r', encoding="UTF-8")
        for text in f:
            msg = text.split('||')
            msgRep = int(msg[2])
            
            if msgRep > 0:
                for entry in self.mostVoted:
                    if entry[0] >= msgRep:
                        continue
                    i = self.mostVoted.index(entry)
                    self.mostVoted.insert(i, (msgRep, msg[1], msg[0]))
                    self.mostVoted.pop()
                    break
                
            elif msgRep < 0:
                for entry in self.leastVoted:
                    if entry[0] <= msgRep:
                        continue
                    i = self.leastVoted.index(entry)
                    self.leastVoted.insert(i, (msgRep, msg[1], msg[0]))
                    self.leastVoted.pop()
                    break
        f.close()
    
    def finalize(self):
        return

    def saveData(self):
        print("Writing to: " + helpers._ratedContentDataLoc)
        f = io.open(helpers._ratedContentDataLoc, 'w+', encoding="UTF-8")
        for entry in self.mostVoted:
            f.write('{0}:{1} - {2}\n'.format(entry[0], entry[1], entry[2]))
        f.write('\n')
        for entry in self.leastVoted:
            f.write('{0}:{1} - {2}\n'.format(entry[0], entry[1], entry[2]))
        f.close()
        
def parseMessages():
    if not os.path.exists(helpers._messagesDataLoc):
        print(helpers._messagesDataLoc + " is not exists!")
        return

    #wordParser = WordCounter()
    #messageParser = MessageParser(wordParser)
    #parsedLines = 0

    #print("Reading from: " + helpers._messagesDataLoc)
    #f = io.open(helpers._messagesDataLoc, 'r', encoding="UTF-8")
    #for text in f:
    #    message = text.split('||')
    #    messageParser.feed(message)
    #    parsedLines += 1
    #    if parsedLines % 100 == 0:
    #        print("Parsed " + str(parsedLines) + " lines")
    #f.close()

    #messageParser.finalize()

    #wordParser = CitationCounter()
    #print("Reading from: " + helpers._quotesDataLoc)
    #f = io.open(helpers._quotesDataLoc, 'r', encoding="UTF-8")
    #for text in f:
    #    t = text.split('||')
    #    wordParser.feed(t[0])
    #f.close()

    #wordParser.finalize()
    #wordParser.saveData()

    #new code
    analyzers = []
    analyzers.append(MostLeastVotedContent())
    analyzers.append(CitationCounter())
    analyzers.append(WordCounter())

    for analyzer in analyzers:
        moduleStartTime = time.time()
        print('-Module {0} is now working.'.format(analyzer.name))
        try:
            analyzer.doWork()
        except BaseException as s:
            print('{0} module is failed on work stage. Error message: {1}'.format(analyzer.name, str(s)))
            continue
        print('-Module {0} is now finalizing.'.format(analyzer.name))
        try:
            analyzer.finalize()
        except BaseException as s:
            print('{0} module is failed on finalizer stage. Error message: {1}'.format(analyzer.name, str(s)))
            continue
        print('-Module {0} is now saving.'.format(analyzer.name))
        try:
            analyzer.saveData()
        except BaseException as s:
            print('{0} module is failed on save stage. Error message: {1}'.format(analyzer.name, str(s)))
            continue
        print('-Module {0} finished work in {1} seconds.'.format(analyzer.name, str(time.time() - moduleStartTime)))    
