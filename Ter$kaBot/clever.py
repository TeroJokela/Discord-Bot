import aiohttp
import json

class CleverBot(object):
    def __init__(self, user, key, nick=None):
        self.user = user
        self.key = key
        self.nick = nick

    async def query(self, text):
        body = {
            'user': self.user,
            'key': self.key,
            'nick': self.nick,
            'text': text
        }

        async with aiohttp.ClientSession() as session:
            async with session.post('https://cleverbot.io/1.0/ask', data=body) as response:
                r = await response.text()

        r = json.loads(r)
        return r['response']
