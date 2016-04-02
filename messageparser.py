import os, io, re, time
import pymorphy2
import helpers
from collections import Counter
from analyzer import Analyzer

morph = pymorphy2.MorphAnalyzer()

replaceRules = {'ии':'и'}
        
class WordCounter(Analyzer):
    def __init__(self):
        self.name = "Frequent words counter"
        self.pattern = re.compile('[\W_]+')
        self.wordsCounter = Counter()
        self.frequentWordsCounter = Counter()
        self.unknownWordsCounter = Counter()

    def doWork(self):
        print("Reading from: " + helpers.allMessagesDataLoc)
        f = io.open(helpers.allMessagesDataLoc, 'r', encoding='UTF-8')
        for text in f:
            msg = text.split('||')
            text = msg[6]
            words = self.pattern.sub(' ', text).split()
            if words is None:
                words = [text]
        
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
        
        print("Reading from: " + helpers.wordFrequencyRuLoc)
        f = io.open(helpers.wordFrequencyRuLoc, 'r', encoding="UTF-8")
        for text in f:
            lemma = text.strip().split(' ')
            frequencyTable[lemma[1]] = float(lemma[0])
        f.close()

        print("Reading from: " + helpers.wordFrequencyEnLoc)
        f = io.open(helpers.wordFrequencyEnLoc, 'r', encoding="UTF-8")
        for text in f:
            lemma = text.strip().split(' ')
            frequencyTable[lemma[1]] = float(lemma[0])
        f.close()
        
        for word in self.wordsCounter.most_common():
            frequency = max(frequencyTable[word[0]], 1)
            self.frequentWordsCounter[word[0]] = round(word[1] * 100000 / frequency)
        
    def saveData(self):
        print("Writing to: " + helpers.wordsDataLoc)
        f = io.open(helpers.wordsDataLoc, 'w+', encoding="UTF-8")
        for word in self.wordsCounter.most_common():
            f.write(str(word[1]) + ":" + word[0] + "\n")
        f.close()

        print("Writing to: " + helpers.unknownWordsDataLoc)
        f = io.open(helpers.unknownWordsDataLoc, 'w+', encoding="UTF-8")
        for word in self.unknownWordsCounter.most_common():
            f.write(str(word[1]) + ":" + word[0] + "\n")
        f.close()

        print("Writing to: " + helpers.frequentWordsDataLoc)
        f = io.open(helpers.frequentWordsDataLoc, 'w+', encoding="UTF-8")
        for word in self.frequentWordsCounter.most_common():
            f.write(str(word[1]) + ":" + word[0] + "\n")
        f.close()

class MostLeastVotedContent(Analyzer):
    def __init__(self):
        self.name = "Most and least rated content"
        self.mostVoted = []
        self.leastVoted = []
        

        for i in range(50):
            self.mostVoted.append((1, "No sender", "No URL"))
            self.leastVoted.append((-1, "No sender", "No URL"))
        
    def doWork(self):
        print("Reading from: " + helpers.allMessagesDataLoc)
        f = io.open(helpers.allMessagesDataLoc, 'r', encoding="UTF-8")
        for text in f:
            msg = text.split('||')
            msgRep = int(msg[4])
            
            if msgRep > 0:
                for entry in self.mostVoted:
                    if entry[0] >= msgRep:
                        continue
                    i = self.mostVoted.index(entry)
                    self.mostVoted.insert(i, (msgRep, msg[3], helpers.getPageURL(msg[0], msg[1], msg[2])))
                    self.mostVoted.pop()
                    break
                
            elif msgRep < 0:
                for entry in self.leastVoted:
                    if entry[0] <= msgRep:
                        continue
                    i = self.leastVoted.index(entry)
                    self.leastVoted.insert(i, (msgRep, msg[3], helpers.getPageURL(msg[0], msg[1], msg[2])))
                    self.leastVoted.pop()
                    break
        f.close()

    def saveData(self):
        print("Writing to: " + helpers.ratedContentDataLoc)
        f = io.open(helpers.ratedContentDataLoc, 'w+', encoding="UTF-8")
        for entry in self.mostVoted:
            f.write('{0}:{1} - {2}\n'.format(entry[0], entry[1], entry[2]))
        f.write('\n')
        for entry in self.leastVoted:
            f.write('{0}:{1} - {2}\n'.format(entry[0], entry[1], entry[2]))
        f.close()

class SimpleIterator(Analyzer):
    rawDataLoc = "Null"
    procDataLoc = "Null"
    dataCont = Counter()
    
    def doWork(self):
        self.dataCont = Counter()
        print("Reading from: " + self.rawDataLoc)
        f = io.open(self.rawDataLoc, 'r', encoding="UTF-8")
        for text in f:
            data = text.split('||')
            self.feedData(data)
        f.close()

    def saveData(self):
        print("Writing to: " + self.procDataLoc)
        f = io.open(self.procDataLoc, 'w+', encoding="UTF-8")
        for word in self.dataCont.most_common():
            f.write(str(word[1]) + ":" + word[0] + "\n")
        f.close()

    def feedData(self, data):
        return

class TopicStartersCounter(SimpleIterator):
    def __init__(self):
        self.name = "Topic starters"
        self.rawDataLoc = helpers.allMessagesDataLoc
        self.procDataLoc = helpers.topicStartersDataLoc
        self.lastTopicID = '0'
        
    def feedData(self, data):
        if self.lastTopicID != data[0]:
            self.dataCont[data[3]] += 1
            self.lastTopicID = data[0]

    def finalize(self):
        self.dataCont['Гость__*'] = -1

class CitationCounter(Analyzer):
    def __init__(self):
        self.name = "Most citated content"
        self.rawDataLoc = helpers.allQuotesDataLoc
        self.procDataLoc = helpers.citationCountDataLoc

    def feedData(self, data):
        dataCont[msg[3]] += 1

#needs for other parsers
class PublicMessagesCounter(SimpleIterator):
    def __init__(self):
        self.name = "Public messages"
        self.rawDataLoc = helpers.allMessagesDataLoc
        self.procDataLoc = helpers.msgsCountDataLoc
        
    def feedData(self, data):
        self.dataCont[data[3]] += 1

class MostWatchedUsersCounter(SimpleIterator):
    def __init__(self):
        self.name = "Most watched users"
        self.rawDataLoc = helpers.allUserdataDataLoc
        self.procDataLoc = helpers.mostWatchedDataLoc

    def feedData(self, data):
        self.dataCont[data[0]] += int(data[4])

class PublicReputationCounter(SimpleIterator):
    def __init__(self):
        self.name = "Public reputation"
        self.rawDataLoc = helpers.allMessagesDataLoc
        self.procDataLoc = helpers.publicRepDataLoc

    def feedData(self, data):
        self.dataCont[data[3]] += int(data[4])

def parseMessages():   
    analyzers = []
    analyzers.append(MostLeastVotedContent())
    analyzers.append(TopicStartersCounter())
    analyzers.append(CitationCounter())
    analyzers.append(PublicMessagesCounter())
    analyzers.append(MostWatchedUsersCounter())
    analyzers.append(PublicReputationCounter())
    #currently disabled due to long runtime
    #analyzers.append(WordCounter())
    

    for analyzer in analyzers:
        moduleStartTime = time.time()
        print('-----')
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

