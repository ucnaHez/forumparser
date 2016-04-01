import tdownloader, pageparser, messageparser, helpers
import os

def main():

    if not os.path.exists(helpers._rawDataLoc):
        os.mkdir(helpers._rawDataLoc)
    if not os.path.exists(helpers._processedDataLoc):
        os.mkdir(helpers._processedDataLoc)
    if os.path.exists(helpers._cookiesDataLoc): 
        helpers.loadPrivateKey()
    else:
        proceed = input("Private key is not found. Only threads that are available anonymously will be downloaded. Proceed? [Y/N]")
        if proceed.lower() != "y":
            print("Shutting down")
            return
    
    tdownloader.downloadUserpages()
    #tdownloader.downloadPages()
    #pageparser.parseData()
    #messageparser.parseMessages()

    

if __name__ == '__main__':
    main()
