'''
    Download a random picture from one of the newest
    pictures uploaded to imgur or by a specific tag
'''
import random
import os
import requests
from urllib import request
from bs4 import BeautifulSoup

class Imgur:
    def downloadRandomPic():
        try:
            # First get the site's source so we can get data from it
            siteSource = requests.get(r'https://imgur.com/new/time')
            siteSourceText = siteSource.text

            # This will hold all the links to the images we can find
            items = []
            soup = BeautifulSoup(siteSourceText, "html.parser")
            for i in soup.find_all('a', {'class': 'image-list-link'}):
                href = i.get('href')
                if href != None:
                    # Add the image link to our 'items' list
                    items.append(href)

            # Choose a random image and download that
            downloadURL = "https://imgur.com" + items[random.randint(1, len(items))]

            # Now we download the picture.
            # We need to get the direct link to the image so we can download it
            siteSourceDownload = requests.get(downloadURL)
            siteSourceDownloadText = siteSourceDownload.text
            soupDownload = BeautifulSoup(siteSourceDownloadText, "html.parser")
            for i in soupDownload.findAll('link', {'rel': 'image_src'}):
                href = i.get('href')
                if href != None:
                    if Imgur.isGif(siteSourceDownloadText, soupDownload) == False:
                        # Download the image from the direct link we found
                        request.urlretrieve(href, r'random.jpg')
                        return True
            return False
        except IndexError:
            print("IndexError!")

    def downloadRandomPicByTag(targetUrl):
        try:
            # First get the site's source so we can get data from it
            siteSource = requests.get(targetUrl)
            siteSourceText = siteSource.text
           
            # This will hold all the links to the images we can find
            items = []
            soup = BeautifulSoup(siteSourceText, "html.parser")
            for i in soup.find_all('a', {'class': 'image-list-link'}):
                href = i.get('href')
                if href != None:
                    # Add the image link to our 'items' list
                    items.append(href)

            downloadURL = "https://imgur.com" + items[random.randint(0, len(items))]

            # Now we download the picture.
            # We need to get the direct link to the image so we can download it
            siteSourceDownload = requests.get(downloadURL)
            siteSourceDownloadText = siteSourceDownload.text
            soupDownload = BeautifulSoup(siteSourceDownloadText, "html.parser")
            for i in soupDownload.findAll('link', {'rel': 'image_src'}):
                href = i.get('href')
                if href != None:
                    if Imgur.isGif(siteSourceDownloadText, soupDownload) == False:
                        request.urlretrieve(href, r'pic.jpg')
                        return True
            return False
        except IndexError:
            print("IndexError!")

    # Check if the image is a GIF or not
    def isGif(sourceText, soup):
        for i in soup.findAll('div', {'class': 'video-elements'}):
            return True
        return False
        
    # Create an Imgur link using the tags we were given
    def createLink(tags):
        fin = ''
        for i in tags:
            if i == ' ':
                fin += '+'
            else:
                fin += i
        return 'https://imgur.com/search/time?q=' + fin
