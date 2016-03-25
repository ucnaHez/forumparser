#OH GOD DO SOMETHING WITH IT!
#IT'S SOOOO BAD!!

#TODO: remove "сказал:"

from html.parser import HTMLParser
from bs4 import BeautifulSoup
from bs4 import NavigableString
from bs4 import Comment
import io, os
import helpers

def isPlainText(c):
    return isinstance(c, NavigableString) and not isinstance(c, Comment)

def findAllTextInBlock(block, exceptClasses = []):
    msgs = []
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
                msgs.extend(findAllTextInBlock(child, exceptClasses))
    return msgs #messages with only quotes

def findData(soup):
    messages = []
    quotes = []
    for div in soup.find_all('div'):
        cls = div.get('class')
        if cls is None:
            continue
        if 'entry-content' in cls:
            #messages
            msg = findAllTextInBlock(div, ['citation', 'quote'])
            messages.extend(msg)                    

            #citations
            p = div.find_all(class_='citation')
            d = div.find_all(class_='quote')
            if p is None or d is None:
                continue
            if len(p) != len(d):
                print("SYNTAX ERROR")
            if len(p) <= 0:
                continue
            for t in range(len(p)):
                nick = ' '.join(findAllTextInBlock(p[t]))
                i = min(nick.find('('), nick.find(u'ска')) #сказал
                if i > 0:
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
        data = findData(soup)

        for msg in data[0]:
            fm.write(msg + "\n")
        for quote in data[1]:
            fq.write(quote[0] + "||" + quote[1] + "\n")
            
        f.close()

        fm.flush()
        fq.flush()
        
        filesParsed += 1
        print("File " + file + " is parsed. [" + str(filesParsed) + "/" + str(filesTotal) + "]")
    fm.close()
    fq.close()
