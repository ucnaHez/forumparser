# -*- coding: UTF-8 -*-
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

class CitationCounter:
    def __init__(self):
        self.name = "Most citated content"
        self.nicknameCounter = Counter()

    def doWork(self):
        print("Reading from: " + helpers.allQuotesDataLoc)
        f = io.open(helpers.allQuotesDataLoc, 'r', encoding="UTF-8")
        for text in f:
            msg = text.split('||')
            self.nicknameCounter[msg[3]] += 1
        f.close()

    def finalize(self):
        return

    def saveData(self):
        print("Writing to: " + helpers.citationCountDataLoc)
        f = io.open(helpers.citationCountDataLoc, 'w+', encoding="UTF-8")
        for word in self.nicknameCounter.most_common():
            f.write(str(word[1]) + ":" + word[0] + "\n")
        f.close()

class MostLeastVotedContent:
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
    
    def finalize(self):
        return

    def saveData(self):
        print("Writing to: " + helpers.ratedContentDataLoc)
        f = io.open(helpers.ratedContentDataLoc, 'w+', encoding="UTF-8")
        for entry in self.mostVoted:
            f.write('{0}:{1} - {2}\n'.format(entry[0], entry[1], entry[2]))
        f.write('\n')
        for entry in self.leastVoted:
            f.write('{0}:{1} - {2}\n'.format(entry[0], entry[1], entry[2]))
        f.close()

class TopicStartersCounter:
    def __init__(self):
        self.name = "Topic starters"
        self.starterCounter = Counter()

    def doWork(self):
        lastTopicID = '0'
        
        print("Reading from: " + helpers.allMessagesDataLoc)
        f = io.open(helpers.allMessagesDataLoc, 'r', encoding="UTF-8")
        for text in f:
            msg = text.split('||')
            if lastTopicID != msg[0] and msg[1] == "000001":
#                if msg[3] == "ucnaHez":
#                    print(msg[0])
                self.starterCounter[msg[3]] += 1
                lastTopicID = msg[0]
        f.close()

    def finalize(self):
        self.starterCounter['Гость__*'] = -1

    def saveData(self):
        print("Writing to: " + helpers.topicStartersDataLoc)
        f = io.open(helpers.topicStartersDataLoc, 'w+', encoding="UTF-8")
        for word in self.starterCounter.most_common():
            f.write(str(word[1]) + ":" + word[0] + "\n")
        f.close()

class UserEfficencyCounter:
    def __init__(self):
        self.name = "Reputation efficency"
        self.efficCounter = Counter()

    def doWork(self):
        print("Reading from: " + helpers.allUserdataDataLoc)
        f = io.open(helpers.allUserdataDataLoc, 'r', encoding="UTF-8")
        for text in f:
            msg = text.split('||')
            if int(msg[4]) >= 50:
                self.efficCounter[msg[0]] = float(msg[3]) / float(msg[4])
        f.close()

    def finalize(self):
        return

    def saveData(self):
        print("Writing to: " + helpers.repEfficencyDataLoc)
        f = io.open(helpers.repEfficencyDataLoc, 'w+', encoding="UTF-8")
        for word in self.efficCounter.most_common():
            f.write("{:.4f}".format(word[1]) + ":" + word[0] + "\n")
        f.close()

class UserRepCounter:
    def __init__(self):
        self.name = "User reputation"
        self.repCounter = Counter()

    def doWork(self):
        print("Reading from: " + helpers.allUserdataDataLoc)
        f = io.open(helpers.allUserdataDataLoc, 'r', encoding="UTF-8")
        for text in f:
            msg = text.split('||')
            self.repCounter[msg[0]] = int(msg[3])
        f.close()

    def finalize(self):
        return

    def saveData(self):
        print("Writing to: " + helpers.userRepDataLoc)
        f = io.open(helpers.userRepDataLoc, 'w+', encoding="UTF-8")
        for word in self.repCounter.most_common():
            f.write(str(word[1]) + ":" + word[0] + "\n")
        f.close()

#needs for other parsers
class PublicMessagesCounter:
    def __init__(self):
        self.name = "Public messages"
        self.msgauthors = Counter()

    def doWork(self):
        print("Reading from: " + helpers.allMessagesDataLoc)
        f = io.open(helpers.allMessagesDataLoc, 'r', encoding="UTF-8")
        for text in f:
            msg = text.split('||')
            self.msgauthors[msg[3]] += 1
        f.close()

    def finalize(self):
        return

    def saveData(self):
        print("Writing to: " + helpers.msgsCountDataLoc)
        f = io.open(helpers.msgsCountDataLoc, 'w+', encoding="UTF-8")
        for word in self.msgauthors.most_common():
            f.write(str(word[1]) + ":" + word[0] + "\n")
        f.close()
    

def parseMessages():   
    analyzers = []
    analyzers.append(MostLeastVotedContent())
    analyzers.append(TopicStartersCounter())
    analyzers.append(CitationCounter())
    analyzers.append(PublicMessagesCounter())
    analyzers.append(UserRepCounter())
    analyzers.append(UserEfficencyCounter())
    #currently disabled due to long runtime
#    analyzers.append(WordCounter())
    

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
        print('-----')
