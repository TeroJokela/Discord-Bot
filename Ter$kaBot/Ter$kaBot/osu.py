'''
    Uses osu!API and gets all the data we can get from a specific user or beatmap
    Documentation for the API can be found here:
    https://github.com/ppy/osu-api/wiki
'''
import json
import requests

# Our API's base URL
apiURL = "https://osu.ppy.sh/api/"

class osu(object):
    def __init__(self, key):
        # "Attach" the key to this object
        self.key = key

    # Gets map's information by ID
    def get_beatmaps(self, beatmapLink):
        # Extract the beatmap ID from the link that we're given
        beatmapID = getID(beatmapLink)

        # Our arguments for the API request
        args = [
            'k=' + str(self.key),
            'b=' + str(beatmapID),
        ]
    
        # Make the API request url using our arguments from 'args'-list
        requestURL = makeLink("get_beatmaps", args)

        # Get the data and return it
        r = requests.post(requestURL)
        r = json.loads(r.text)
        return r[0]

    # Gets user's information by username or ID
    # First, we try to get the user data via an ID, but if they pass in a string we get IndexError or ValueError
    # If we get either of those, we will get the data via an ID (still the same argument that got passed in) 
    def get_user(self, userLink):
        try:
            # Extract the user ID from the link that we're given
            userID = getID(userLink)

            # Our arguments for the API request
            args = [
                'k=' + str(self.key),
                'u=' + str(userID),
                'type=id'
            ]
    
            # Make the API request url using our arguments from 'args'-list
            requestURL = makeLink("get_user", args)

            # Get the data and return it
            r = requests.get(requestURL)
            r = json.loads(r.text)
            return r[0]

        # This is if we get an error, which usually means that the user inputted an username rather than
        # an ID, this will return the same data expect we find the user by username
        except IndexError:
            # Extract the username from the link that we're given
            username = getUsername(userLink)

            # Our arguments for the API request
            args = [
                'k=' + str(self.key),
                'u=' + str(username),
                'type=sting'
            ]
    
            # Make the API request url using our arguments from 'args'-list
            requestURL = makeLink("get_user", args)

            # Get the data and return it
            r = requests.get(requestURL)
            r = json.loads(r.text)
            return r[0]

        except ValueError:
            # Extract the username from the link that we're given
            username = getUsername(userLink)

            # Our arguments for the API request
            args = [
                'k=' + str(self.key),
                'u=' + str(username),
                'type=sting'
            ]
    
            # Make the API request url using our arguments from 'args'-list
            requestURL = makeLink("get_user", args)

            # Get the data and return it
            r = requests.get(requestURL)
            r = json.loads(r.text)
            return r[0]

# Takes the items from 'listOfArgs' and adds them to the API link so we can get data from it
def makeLink(toWhere, listOfArgs):
    URL = apiURL + toWhere + "?"

    for i in listOfArgs:
        URL += (i + "&")

    return URL[:-1]

# This is just to make it print the API output so it can be read easily
def printBetter(whatever):
    string = str(whatever)
    newString = ""

    for i in string:
        if i == ",":
            newString += ",\n"
        else:
            newString += i

    return newString

# Here we get the user's username from the link if it's not an ID
def getUsername(link):
    _username = str(link[21:])
    username = ""

    for i in _username:
        if i == "/" or i == " ":
            break
        else:
            username += i

    return username

# Here we get the user's ID from the link if it's not a string
def getID(link):
    _ID = str(link[21:])
    ID = ""

    for i in _ID:
        if i.isdigit():
            ID += i
        else:
            break
        
    return int(ID)
