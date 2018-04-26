import requests
import json

class CleverBot(object):
    def __init__(self, user, key, nick=None):
        self.user = user
        self.key = key
        self.nick = nick

        body = {
            'user': user,
            'key': key,
            'nick': nick
        }

        requests.post('https://cleverbot.io/1.0/create', json=body)


    def query(self, text):
        body = {
            'user': self.user,
            'key': self.key,
            'nick': self.nick,
            'text': text
        }

        try:
            r = requests.post('https://cleverbot.io/1.0/ask', json=body, timeout=20)
        except requests.exceptions.ReadTimeout:
            return False    
        
        r = json.loads(r.text)

        if r['status'] == 'success':
            return r['response']
        else:
            return False
