# -*- coding: UTF-8 -*-

#OH GOD DO SOMETHING WITH IT!
#IT'S SOOOO BAD!!
#-Done
#Fix this rep bug!
#-It caused by bug in bs4. It's reads corrupted block not until the end but until not opened closing tag.

from html.parser import HTMLParser
from bs4 import BeautifulSoup
from bs4 import NavigableString
from bs4 import Comment
import io, os, time
import helpers

errorOutput = io.open('error.txt', 'w+', encoding='UTF-8')

def isPlainText(c):
    return isinstance(c, NavigableString) and not isinstance(c, Comment)

def findAllTextInBlock(block, exceptClasses = [], currentDepth = 1, maxDepth = 10):
    msgs = []
    if currentDepth >= maxDepth:
        return msgs
    for child in block.children:
        if isPlainText(child):
            text = child.string.replace("\n", " ")
            text = text.strip()
            if not text.isspace() and len(text) > 0:
                msgs.append(text)
        elif isinstance(child, Comment):
            continue
        else:
            t = child.get('class')
            if t is None:
                t = []
            merge = [i for i in t if i in exceptClasses]
            if len(merge) <= 0:
                msgs.extend(findAllTextInBlock(child, exceptClasses, currentDepth + 1))
    return ''.join(msgs)

def getDataFromPosts(soup, fileName):
    messages = []
    quotes = []
    for postblock in soup.find_all(class_="post_block"):
        postbody = postblock.find(class_="post_body")

        #name
        authorinfo = postblock.find(class_="user_details")
        authorname = findAllTextInBlock(authorinfo.span)
        
        #id
        postid = postblock.get('id')[8:]
        
        #messages
        post = postbody.find(class_="entry-content")
        msg = findAllTextInBlock(post, ['citation', 'quote'])

        #reputation
        repblock = postbody.find(class_="rep_bar")
        if repblock is None:
            rep = 0
#            errorOutput.write("No reputation error in {0}! Message ID: {1}\n".format(fileName, postid))	fuck disabled rep
 #           errorOutput.flush()
        else:
            rep = findAllTextInBlock(repblock).replace(' ', '')

        #time
        infoblock = postbody.find(class_="posted_info")
        timeblock = infoblock.find(class_="published")
        timestr = timeblock.get('title')
        #ptime = time.strptime(timestr, "%Y-%m-%dT%H:%M:%S+00:00")
        
        messages.append((postid, authorname, rep, timestr, msg))
        
        #quotes
        p = post.find_all(class_='citation')
        d = post.find_all(class_='quote')
        
        if not p is None and not d is None:
            if len(p) != len(d):
                errorOutput.write("Trouble with quotes in {0}! Message ID: {1}\n".format(fileName, postid))
                errorOutput.flush()
            else:
                for t in range(len(p)):
                    nick = findAllTextInBlock(p[t])
                    i = nick.find('(')
                    i2 = nick.find(':')
                    if i > 0 or i2 > 0:
                        if i < 0:
                            nick = nick[:i2 - 7]
                        else:
                            nick = nick[:i - 1]
                            
                        text = findAllTextInBlock(d[t])
                        if text.isspace() or nick.isspace():
                            print("Data not found: " + str(nick) + " - " + str(text))
                        else:
                            quotes.append((postid, nick, text))
                        
    return (messages, quotes)

def getDataFromUserpage(soup, fileName):
    data = []
    nickblock = soup.find(class_="nickname")
    nick = findAllTextInBlock(nickblock)
    
    statblock = soup.find(class_="ipsList_data")
    rows = statblock.find_all(class_="row_data")
    group =         findAllTextInBlock(rows[0])
    msgsCount =     findAllTextInBlock(rows[1])
    watchedTimes =  findAllTextInBlock(rows[2])
    
    return (nick, group, msgsCount, watchedTimes)

def parsePages():
    if not os.path.exists(helpers.processedDataLoc):
        os.mkdir(helpers.processedDataLoc)
        print(helpers.processedDataLoc)
    if not os.path.exists(helpers.messagesDataLoc):
        os.mkdir(helpers.messagesDataLoc)
    if not os.path.exists(helpers.quotesDataLoc):
        os.mkdir(helpers.quotesDataLoc)
    
    allFiles = []
    if not os.path.exists(helpers.rawTopicsDataLoc):
        print(helpers.rawDataLoc + " is not found!")
        return False
    for file in os.listdir(helpers.rawTopicsDataLoc):
        if file.endswith(".html"):
            allFiles.append(file)

    filesParsed = 0   
    filesTotal = len(allFiles)
    
    print("Found " + str(filesTotal) + " files total.")

    for file in allFiles:
        sname = file[:-5]
        
        f = io.open('{0}/{1}'.format(helpers.rawTopicsDataLoc, file), encoding="UTF-8")
        fm = io.open('{0}/{1}.txt'.format(helpers.messagesDataLoc, sname), 'w+',encoding="UTF-8")
        fq = io.open('{0}/{1}.txt'.format(helpers.quotesDataLoc, sname), 'w+',encoding="UTF-8")
        
        text = f.read().replace('||','')
        
        soup = BeautifulSoup(text, 'html.parser')
        data = getDataFromPosts(soup, file)

        topicInfo = file.split('.')
                
        for msg in data[0]:
            #0)topic number, 1)page number, 2)post id, 3)author name, 4)reputation, 5)post data, 6)message
            fm.write("{0}||{1}||{2}||{3}||{4}||{5}||{6}\n".format(topicInfo[0], topicInfo[1], msg[0], msg[1], msg[2], msg[3], msg[4]))
        for quote in data[1]:
            #0)topic nubmer, 1)page number, 2)post id, 3)citated author name, 4)citation
            fq.write("{0}||{1}||{2}||{3}||{4}\n".format(topicInfo[0], topicInfo[1], quote[0], quote[1], quote[2]))
            
        f.close()
        fm.close()
        fq.close()

        filesParsed += 1
        print("File " + file + " is parsed. [" + str(filesParsed) + "/" + str(filesTotal) + "]")

    print("Finalizing...")
    fm = io.open(helpers.allMessagesDataLoc, 'w+', encoding='UTF-8')
    for file in os.listdir(helpers.messagesDataLoc):
        if not file.endswith(".txt"):
            continue
        f = io.open('{0}/{1}'.format(helpers.messagesDataLoc, file), encoding='UTF-8')
        for line in f:
            fm.write(line)
    fm.close()
    fq = io.open(helpers.allQuotesDataLoc, 'w+', encoding='UTF-8')
    for file in os.listdir(helpers.quotesDataLoc):
        if not file.endswith(".txt"):
            continue
        f = io.open('{0}/{1}'.format(helpers.quotesDataLoc, file), encoding='UTF-8')
        for line in f:
            fq.write(line)
    fq.close()
    print("Completed!")

def parseUserpages():
    if not os.path.exists(helpers.processedDataLoc):
        os.mkdir(helpers.processedDataLoc)

    allFiles = []
    if not os.path.exists(helpers.rawUserpagesDataLoc):
        print(helpers.rawUserpagesDataLoc + " is not found!")
        return False
    for file in os.listdir(helpers.rawUserpagesDataLoc):
        if file.endswith(".html"):
            allFiles.append(file)

    filesParsed = 0   
    filesTotal = len(allFiles)

    print("Found " + str(filesTotal) + " files total.")

    fp = io.open(helpers.allUserdataDataLoc, 'w+',encoding="UTF-8")
    for file in allFiles:
        sname = file[:-5]
        
        f = io.open('{0}/{1}'.format(helpers.rawUserpagesDataLoc, file), encoding="UTF-8")

        text = f.read().replace('||','')
        soup = BeautifulSoup(text, 'html.parser')

        data = getDataFromUserpage(soup, file)
        fp.write('{0}||{1}||{2}||{3}||{4}\n'.format(data[0], sname, data[1], data[2], data[3]))        
        fp.flush()
        
        f.close()
        
        filesParsed += 1
        print("File " + file + " is parsed. [" + str(filesParsed) + "/" + str(filesTotal) + "]")

    fp.close()
    print("Completed!")

#parsePages()
#parseUserpages()
