#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import tdownloader, pageparser, messageparser, helpers
import os

def main():

    if not os.path.exists(helpers.rawDataLoc):
        os.mkdir(helpers.rawDataLoc)
    if not os.path.exists(helpers.processedDataLoc):
        os.mkdir(helpers.processedDataLoc)
    if os.path.exists(helpers.cookiesDataLoc): 
        helpers.loadPrivateKey()
    else:
        proceed = input("Private key is not found. Only threads that are available anonymously will be downloaded. Proceed? [Y/N]")
        if proceed.lower() != "y":
            print("Shutting down")
            return
    
   # tdownloader.downloadUserpages()
  #  #tdownloader.downloadPages()
 #   pageparser.parseUserpages()
#    messageparser.parseMessages()

    tdownloader.downloadPages()
    pageparser.parsePages()
    tdownloader.downloadUserpages()
    pageparser.parseUserpages()
    messageparser.parseMessages()
    

if __name__ == '__main__':
    main()
