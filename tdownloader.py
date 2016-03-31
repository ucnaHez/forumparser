#Требуется рефакторинг
#Требуется оптимизация кода скачивания

import io, os, time, requests, requests_cache, threading
import helpers

requests_cache.install_cache('__forum.ss13.ru')

s = requests.session()
s.keep_alive = False

def makeRequest(address, cookies = helpers._cookies):
    try:
        r = requests.get(address, cookies=cookies)
    except BaseException as s:
        print(address + " - " + str(s))
        return None
    return r

def getMessagePagesAsync(topicPagesToDownload):
    retry = 0
    while len(topicPagesToDownload) > 0:
        dnext = topicPagesToDownload.pop()
        if retry > 5:
            if len(topicPagesToDownload) > 0:
                retry = 0
                dnext = topicPagesToDownload.pop()
            else:
                return

        if os.path.exists('{0}\\{1}'.format(helpers._rawTopicsDataLoc, helpers.getPageFilename(dnext[0], dnext[1]))):
            print("{0} is already exists!\n".format(helpers.getPageFilename(dnext[0], dnext[1])), end='')
            retry = 0
            topicPagesToDownload.append((dnext[0], dnext[1] + 1))
            continue
        
        page = makeRequest(helpers.getPageURL(dnext[0], dnext[1]))
        
        if page is None:
            retry += 1
            topicPagesToDownload.append(dnext)
            continue

        if helpers.isNoAccessToPage(page.text):
            retry = 0
            continue

        if helpers.isPageNotExists(page.text):
            retry = 0
            continue

        if helpers.isErrorPage(page.text):
            retry += 1
            topicPagesToDownload.append(dnext)
            continue

        retry = 0
        topicPagesToDownload.append((dnext[0], dnext[1] + 1))
        
        if not os.path.exists(helpers._rawTopicsDataLoc):
            os.mkdir(helpers._rawTopicsDataLoc)
        f = io.open(helpers._rawTopicsDataLoc + "\\" + helpers.getPageFilename(dnext[0], dnext[1]), "w+", encoding="UTF-8")
        f.write(page.text)
        f.close()

        print("Page {0} of topic {1} were saved to {2}\n".format(dnext[1], dnext[0], helpers.getPageFilename(dnext[0], dnext[1])), end='')

def getUserpagesAsync(userpagesToDownload):
    while len(userpagesToDownload) > 0:
        dnext = userpagesToDownload.pop()
        
        if os.path.exists('{0}\\{1}'.format(helpers._rawUserPageDataLoc, helpers.getUserpageFilename(dnext))):
            print("{0} is already exists!\n".format(helpers.getUserpageFilename(dnext)), end='')
            continue

        page = makeRequest(helpers.getUserpageURL(dnext))

        if not os.path.exists(helpers._rawUserPageDataLoc):
            os.mkdir(helpers._rawUserPageDataLoc)
        f = io.open('{0}\\{1}'.format(helpers._rawUserPageDataLoc, helpers.getUserpageFilename(dnext)), "w+", encoding="UTF-8")
        f.write(page.text)
        f.close()

        print("Userpage {0} were saved to {1}\n".format(dnext, helpers.getUserpageFilename(dnext)), end='') 

def downloadDataAsync(method, args):
    activeThreads = []
    downloadingStarted = time.time()

    for threads in range(helpers._threadCount):
        t = threading.Thread(target=method, args=(args,))
        t.start()
        activeThreads.append(t)

    for t in activeThreads:
        t.join()

    print("Downloading is completed in " + helpers.timeSince(downloadingStarted) + "!")

#public members
def downloadPages():
    topicsToDownload = []

    for i in range(1, helpers._topicCount + 1):
        topicsToDownload.insert(0, (i, 1))

    downloadDataAsync(getMessagePagesAsync, topicsToDownload)

def downloadUserpages():
    userpagesToDownload = []

    for i in range(1, helpers._usersCount + 1):
        userpagesToDownload.insert(0, i)

    downloadDataAsync(getUserpagesAsync, userpagesToDownload)
