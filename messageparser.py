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

class UserWordsAnalyzer(Analyzer):
    def __init__(self):
        self.name = "User words"
        self.pattern = re.compile('[\W_]+')

    def doWork(self):
        usersToAnalyze = []
        print("Reading from: " + helpers.msgsCountDataLoc)
        f = io.open(helpers.msgsCountDataLoc, 'r', encoding='UTF-8')
        i = 0
        for line in f:
            if i > 20:
                continue
            i += 1
            data = line.split(':')
            usersToAnalyze.append(data[1].strip().replace('*', ''))
        f.close()

        if not os.path.exists(helpers.personalDataLoc):
            os.mkdir(helpers.personalDataLoc)

        usersdata = []
        for username in usersToAnalyze:
            usersdata.append(self.analyzeUser(username))

        compiledWords = Counter()
        for d in usersdata:
            for w in d[1].most_common():
                compiledWords[w[0]] += w[1]
                
        
        usagePercData = {}
        for d in usersdata:
            usagePercData[d[0]] = Counter()
        
        for w in compiledWords.most_common():
            #usersPerc = {}
            #for d in usersdata:
            #    usersPerc[d[0]] = d[1][w[0]][1] / w[1]
            for d in usersdata:
                #print(type(d))
                #print(type(usagePercData))
                #print(type(usagePercData[d[0]]))
                #print(type(w))
                #print(type(d[1]))
                #print(type(d[1][w[0]]))
                t = d[1][w[0]] / w[1]
                if t > 0:
                    usagePercData[d[0]][w[0]] = t

        for d in usersdata:
            data = usagePercData[d[0]]
            print("Writing to: {0}\\{1}_perc.txt".format(helpers.personalDataLoc, d[0]))
            f = io.open('{0}\\{1}_perc.txt'.format(helpers.personalDataLoc, d[0]), 'w+', encoding='UTF-8')
            for w in data.most_common():
                f.write('{0}:{1}\n'.format(w[1], w[0]))
            f.close()                
        

    def analyzeUser(self, username):
        userWords = Counter()
        print("Reading from: " + helpers.allMessagesDataLoc)
        f = io.open(helpers.allMessagesDataLoc, 'r', encoding='UTF-8')
        for line in f:
            data = line.split('||')
            if data[3] != username:
                continue
            
            text = data[6]
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
                if word in userWords:
                    userWords[word] += 1
                else:
                    p = morph.parse(word)
                    # S:
                    n = p[0].normal_form.replace('ё', 'е')
                    userWords[n] += 1
        f.close()

        totalWords = 0
        
        print("Writing to: {0}\\{1}.txt".format(helpers.personalDataLoc, username))
        fp = io.open('{0}\\{1}.txt'.format(helpers.personalDataLoc, username), 'w+', encoding='UTF-8')
        for word in userWords.most_common():
            fp.write(str(word[1]) + ":" + word[0] + "\n")
        fp.close()

        return (username, userWords)

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
    #analyzers.append(MostLeastVotedContent())
    #analyzers.append(TopicStartersCounter())
    #analyzers.append(CitationCounter())
    #analyzers.append(PublicMessagesCounter())
    #analyzers.append(MostWatchedUsersCounter())
    #analyzers.append(PublicReputationCounter())
    #currently disabled due to long runtime
    #analyzers.append(WordCounter())
    analyzers.append(UserWordsAnalyzer())
    

    for analyzer in analyzers:
        moduleStartTime = time.time()
        print('-----')
        print('-Module {0} is now working.'.format(analyzer.name))
        #try:
        analyzer.doWork()
        #except BaseException as s:
        #    print('{0} module is failed on work stage. Error message: {1}'.format(analyzer.name, str(s)))
        #    continue
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
