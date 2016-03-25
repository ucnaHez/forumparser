from html.parser import HTMLParser
from bs4 import BeautifulSoup
from bs4 import NavigableString
from bs4 import Comment
import io, os
import helpers

_saveDir = "processedData"
_rawDir = "rawData"
_saveFile = "messages.txt"

def getPlainMessages(soup):
    messages = []
    for div in soup.find_all('div'):
        cls = div.get('class')
        if cls == None:
            continue
        if 'entry-content' in cls:
            for child in div.children:
                if not isinstance(child, NavigableString) or isinstance(child, Comment):
                    continue
                text = child.string.replace("\n", " ")
                text = text.strip()
                if text.isspace() or len(text) <= 0:
                    continue
                messages.append(text)

    return messages

def saveMessages(msgs):
    f = io.open(_saveDir + "\\" + _saveFile, 'a+', encoding="UTF-8")
    for msg in msgs:
        f.write((msg + "\n"))
    f.close()

def parseData():   
    if os.path.exists(helpers._messagesDataLoc):
        os.remove(helpers._messagesDataLoc)
        print("Old " + _saveFile + " is removed.")
    
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

    
    for file in allFiles:
        f = io.open(helpers._rawDataLoc + "\\" + file, encoding="UTF-8")
        text = f.read()
        soup = BeautifulSoup(text, 'html.parser')
        msgs = getPlainMessages(soup)
        saveMessages(msgs)
        f.close()
        filesParsed += 1
        print("File " + file + " is parsed. [" + str(filesParsed) + "/" + str(filesTotal) + "]")           
