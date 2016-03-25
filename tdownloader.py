#Требуется рефакторинг
#Требуется оптимизация кода скачивания
#Требуется научить requests логиниться

import io, os, time, requests, requests_cache, threading
import helpers

requests_cache.install_cache('__forum.ss13.ru')

_topicURL = "http://forum.ss13.ru/index.php?showtopic="
_topicSubpageDelimiter = "&st="
_topicSubpageCountMod = 20
_startTime = time.time()

def makeRequest(address):
    try:
        r = requests.get(address, cookies=helpers._cookies)
    except BaseException as s:
        print(address + " - " + str(s))
        return None
    return r

def getTopic(id, page):
    return makeRequest(buildPageReference(id, page))

def saveTopic(request, id, page):   
    if not os.path.exists(helpers._rawDataLoc):
        os.mkdir(helpers._rawDataLoc)
    #print("Writing to: " + helpers._rawDataLoc)
    f = io.open(helpers._rawDataLoc + "\\" + str(id) + "." + str(page) + ".html", "w", encoding="UTF-8")
    f.write(request.text)
    f.close()

def reportCompletion(id, pages):
    timePassed = helpers.timeSince(_startTime)
    print("[" + timePassed + "] Access to topic " + str(id) + " successed. Total " + str(pages - 1) + " pages are downloaded.\n", end="")

def reportFailure(id, pages):
    timePassed = helpers.timeSince(_startTime)
    print("[" + timePassed + "] Access to " + str(id) + " failed on page " + str(pages) + ".\n", end="")

def reportCustom(text):
    timePassed = helpers.timeSince(_startTime)
    print("[" + timePassed + "] " + text + "\n", end="")

def reportCacheFixing(id):
    print("Cached data of topic " + id + " is fixed.")

def buildPageReference(id, page):
    return _topicURL + str(id) + _topicSubpageDelimiter + str((page - 1) * _topicSubpageCountMod)

def getNextTopic():
    global currentTopicID
    global maxTopicCount

    tls = threading.local()
    tls.started_call = time.time()
    tls.ended_call = time.time()
    
    while currentTopicID < maxTopicCount:
        tls.started_call = time.time()
        
        localID = currentTopicID = currentTopicID + 1
        cmpl = getAndSaveSubPages(localID)
        
        if cmpl[0] == True:
            if cmpl[1] == -1:
                reportFailure(localID, cmpl[1])
            else:
                reportCompletion(localID, cmpl[1])
        else: #something wrong with connection. Let's slow our pace
            time.sleep(5)
            cmpl = getAndSaveSubPages(localID, cmpl[1])
            if cmpl[0] == True:
                if cmpl[1] == -1:
                    reportFailure(localID, cmpl[1])
                else:
                    reportCompletion(localID, cmpl[1])
            else:
                reportFailure(localID, cmpl[1])
                time.sleep(10)
                
        tls.finished_call = time.time()

def getAndSaveSubPages(id, frompage = 1):
    page = frompage
    while True:
        request = getTopic(id, page)
        if request is None:
            return (False, page)

        if helpers.isNoAccessToPage(request.text):
            return (True, -1)
        
        if helpers.isPageNotExists(request.text):
            return (True, page)

        #hotfix S:
        if helpers.isErrorPage(request.text):
            return (True, page)

        saveTopic(request, id, page)
        
        reportCustom("Downloaded page " + str(page) + " of topic " + str(id) + ".")
        page = page + 1

def download_cache():
    global currentTopicID
    currentTopicID = 0

    global maxTopicCount
    maxTopicCount = helpers._topicCount   

    active_threads = []

    for topicNum in range(helpers._threadCount): #thread jobs
        t = threading.Thread(target=getNextTopic)
        t.start()

        active_threads.append(t)

    for t in active_threads: #close them as fast as they finished their job
        t.join()

    print("Completed in " + helpers.timeSince(_startTime) + "!")

#def validate_cache():
#    if os.path.exists(_dataLoc):
#        for id in range(_maxTopicCount):
#            if not os.path.exists(_dataLoc + "\\" + str(id) + ".html"):
#                while not getAndSaveTopicByID(id):
#                    print("Could not retrieve topic " + str(id))
#                    time.sleep(1)
#                reportCacheFixing(str(id))
#        print("Data validated!")
#    else:
#        print(_dataLoc + " path is not exists")
