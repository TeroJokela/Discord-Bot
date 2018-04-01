''' 
    Downloads a random picture from 4chan/e...
    I'm pretty ashamed of this to be honest
'''
import random
import requests
from urllib import request
from bs4 import BeautifulSoup

def downloadRandomNSFWAnimePic(): # God someone please help me
    # Get the site's source and get data from it
    siteSource = requests.get('http://boards.4chan.org/e/')
    siteSourceText = siteSource.text

    # This will hold all the direct links to the pictures that we can find
    links = []
    soup = BeautifulSoup(siteSourceText, "html.parser")
    for i in soup.find_all('a', {'class': 'fileThumb'}):
        href = i.get('href')
        if href != None:
            links.append(href)
    
    # Return a random picture chosen from the list
    return 'http://' + links[random.randint(0, len(links) - 1)][2:]
