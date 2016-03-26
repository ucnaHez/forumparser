#OH GOD DO SOMETHING WITH IT!
#IT'S SOOOO BAD!!

from html.parser import HTMLParser
from bs4 import BeautifulSoup
from bs4 import NavigableString
from bs4 import Comment
import io, os, time
import helpers

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

def getDataFromPosts(soup):
    messages = []
    quotes = []
    for postbody in soup.find_all(class_="post_body"):
        #messages
        post = postbody.find(class_="entry-content")
        msg = findAllTextInBlock(post, ['citation', 'quote'])

        #reputation
        repblock = postbody.find(class_="rep_bar")
        rep = findAllTextInBlock(repblock).replace(' ', '')

        #time
        infoblock = postbody.find(class_="posted_info")
        timeblock = infoblock.find(class_="published")
        timestr = timeblock.get('title')
        #ptime = time.strptime(timestr, "%Y-%m-%dT%H:%M:%S+00:00")
        
        messages.append((rep, timestr, msg))
        
        #quotes
        p = post.find_all(class_='citation')
        d = post.find_all(class_='quote')
        
        if not p is None and not d is None:
            for t in range(len(p)):
                nick = ' '.join(findAllTextInBlock(p[t]))
                i = nick.find('(')
                i2 = nick.find(':')
                if i > 0 or i2 > 0:
                    if i < 0:  
                        nick = nick[:i2 - 7]
                    else:
                        nick = nick[:i - 1]

                    text = ' '.join(findAllTextInBlock(d[t]))
                    if text.isspace() or nick.isspace():
                        print("Data not found: " + str(nick) + " - " + str(text))
                    else:
                        quotes.append((nick, text))
        
            

    return (messages, quotes)

def parseData():   
    if os.path.exists(helpers._messagesDataLoc):
        os.remove(helpers._messagesDataLoc)
        print("Old " + helpers._messagesDataLoc + " is removed.")
    
    allFiles = []
    if not os.path.exists(helpers._rawDataLoc):
        print(helpers._rawDataLoc + " is not found!")
        return False
    for file in os.listdir(helpers._rawDataLoc):
        if file.endswith(".html"):
            allFiles.append(file)

    filesParsed = 0   
    filesTotal = len(allFiles)
    
    print("Found " + str(filesTotal) + " files total.")

    fm = io.open(helpers._messagesDataLoc, 'w+',encoding="UTF-8")
    fq = io.open(helpers._quotesDataLoc, 'w+',encoding="UTF-8")
    for file in allFiles:
        f = io.open(helpers._rawDataLoc + "\\" + file, encoding="UTF-8")
        
        text = f.read()
        soup = BeautifulSoup(text, 'html.parser')

        data = getDataFromPosts(soup)

        for msg in data[0]:
            fm.write("{3}||{0}||{1}||{2}\n".format(msg[0], msg[1], msg[2], file))
        for quote in data[1]:
            fq.write("{0}||{1}\n".format(quote[0], quote[1]))
            
        f.close()

        fm.flush()
        fq.flush()
        
        filesParsed += 1
        print("File " + file + " is parsed. [" + str(filesParsed) + "/" + str(filesTotal) + "]")

    fm.close()
    fq.close()

parseData()
