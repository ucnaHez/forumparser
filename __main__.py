import tdownloader, pageparser, messageparser, helpers
import os

def main():

    if not os.path.exists(helpers._rawDataLoc):
        os.mkdir(helpers._rawDataLoc)
    if not os.path.exists(helpers._processedDataLoc):
        os.mkdir(helpers._processedDataLoc)
    
    #tdownloader.download_cache()
    #pageparser.parseData()
    messageparser.parseMessages()
    

if __name__ == '__main__':
    main()
