import json
import requests
from urllib import request
from urllib.parse import quote
import random

# Our API's base URL
apiURL = "https://www.googleapis.com/customsearch/v1"

class gAPI(object):
    def __init__(self, APIKey, cxKey):
        self.APIKey = APIKey
        self.cxKey = cxKey.replace(":", "%")

    def requestImages(self, tag):
        tag = quote(tag, safe='') # Make "tag" URL-safe

        args = [
            "q=" + tag,
            "key=" + self.APIKey,
            "cx=" + self.cxKey,
            "filter=1",
            "searchType=image",
			"safe=off"
        ]

        URL = apiURL + "?"

        for i in args:
            URL += (i + "&")

        r = requests.get(URL)
        r = json.loads(r.text)
        return r

    def downloadRandomPicture(self, tag):
        dic = self.requestImages(tag)
        try:
            listItems = dic['items']
        except KeyError:
            try:
                if dic['error']['errors'][0]['reason'] == 'dailyLimitExceeded':
                    return "No_Requests_Left"
            except KeyError:
                return "No_Results"
        
        pictureLinks = []
        for i in listItems:
            if i['image']['byteSize'] < 8000000:
                pictureLinks.append(i['link'])

        return pictureLinks[random.randint(0, len(pictureLinks) - 1)]

if __name__ == '__main__':
    print(API.downloadRandomPicture(input("> ")))
