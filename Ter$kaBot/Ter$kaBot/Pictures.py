import random
import requests
from urllib import request
from bs4 import BeautifulSoup

def downloadRandomPic(targetUrl):
    siteSource = requests.get(targetUrl)
    siteSourceText = siteSource.text

    items = []
    soup = BeautifulSoup(siteSourceText, "html.parser")
    for i in soup.find_all('a', {'class': 'image-list-link'}):
        href = i.get('href')
        if href != None:
            items.append(href)

    downloadURL = "https://imgur.com" + items[random.randint(0, len(items))]

    #Now we download the picture
    siteSourceDownload = requests.get(downloadURL)
    siteSourceDownloadText = siteSourceDownload.text
    soupDownload = BeautifulSoup(siteSourceDownloadText, "html.parser")
    for i in soupDownload.findAll('link', {'rel': 'image_src'}):
        href = i.get('href')
        if href != None:
            finalFilename = str(random.randint(0, 999))
            if isGif(siteSourceDownloadText, soupDownload) == True:
                break
            request.urlretrieve(href, r'pic.jpg')
            return True
    return False

def isGif(sourceText, soup):
    for i in soup.findAll('div', {'class': 'video-elements'}):
        return True
    return False

