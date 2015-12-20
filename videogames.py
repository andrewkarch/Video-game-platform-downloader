# The MIT License (MIT)

# Copyright (c) 2015 Andrew Karch

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from xml.dom import minidom #parsing Game XML
import urllib2 #Downloading game xml
import sys #Handles the write and encoding
import string #used for processing of the strings
import os #File Management
import platform #Current OS
import time #Calculate Run time
from difflib import SequenceMatcher #Fuzzy Search

#Change default encoding to UTF-8
reload(sys)
sys.setdefaultencoding('UTF8')

#Creates the Base URL, the game's name will be appended to this
api_key = "" # Get one here: https://auth.giantbomb.com/signup/
feild_list_array = ["genres", "name", "platforms", "expected_release_year", "original_release_date"] #The fields to get from the database
baseURL = 'http://www.giantbomb.com/api/search/?api_key=' + api_key + '&format=xml&query=\''

#Counts and totals
failedGameCount = 0
errorCount = 0
succeededGameCount = 0
numberofGames = 0
count = 1

#initializing the values used for the fuzzy search
similarity = 0
similarityFound = False
similarityThreshold = 0.9


errorString = "" #string to store errors
outputString = "" #string to store the output

preferredPlatformArray = [] #Array to store the platforms in order of preference


#Check for required files
if not os.path.isfile("PlatformList.txt"):
    print "Using default platform list"
    preferredPlatformArray = ["3DO", "Acorn Archimedes", "Action Max", "Adventure Vision", "Amazon Fire TV", "Amiga", "Amiga CD32", "Amstrad CPC", "Android", "Apple II", "Apple IIgs", "Aquarius", "Arcade",
    "Arcadia 2001", "Atari 2600", "Atari 5200", "Atari 7800", "Atari 8-bit", "Atari Lynx", "Atari ST", "Bally Astrocade", "Bandai Playdia", "BBC Micro", "Browser", "Casio Loopy", "Casio PV-1000", "CD-i",
    "Channel F", "ColecoVision", "Commodore 128", "Commodore 16", "Commodore 64", "Commodore CDTV", "Commodore PET/CBM", "Dragon 32/64", "Dreamcast", "DSiWare", "Epoch Cassette Vision", "Famicom Disk System",
    "FM Towns", "FM-7", "Game Boy", "Game Boy Advance", "Game Boy Color", "Game Gear", "Game Wave", "Game.Com", "GameCube", "GamePark 32", "Genesis", "Gizmondo", "HyperScan", "Intellivision", "iPad", "iPhone",
    "iPod", "Jaguar", "Leapfrog Didj", "Leapster", "Linux", "Mac", "Mega Duck", "Memorex MD 2500 VIS", "Microvision", "MSX", "N-Gage", "NEC PC-6001", "NEC PC-8801", "NEC PC-9801", "Neo Geo", "Neo Geo CD",
    "Neo Geo Pocket", "Neo Geo Pocket Color", "New Nintendo 3DS", "Nintendo 3DS", "Nintendo 3DS eShop", "Nintendo 64", "Nintendo 64DD", "Nintendo DS", "Nintendo Entertainment System", "Nintendo NX (working title)",
    "NUON", "Odyssey", "Odyssey 2", "Ouya", "PC", "PC-FX", "Pinball", "Pioneer LaserActive", "Pippin", "PLATO", "PlayStation", "PlayStation 2", "PlayStation 3", "PlayStation 4", "PlayStation Network (PS3)",
    "PlayStation Network (PSP)", "PlayStation Network (Vita)", "PlayStation Portable", "PlayStation Vita", "R-Zone", "RCA Studio II", "RDI Halcyon", "Satellaview", "Saturn", "Sega 32X", "Sega CD",
    "Sega Master System", "Sega Pico", "Sega SG-1000", "Sharp MZ", "Sharp X1", "Sharp X68000", "Super A'Can", "Super Cassette Vision", "Super Nintendo Entertainment System", "SuperGrafx", "TI-99/4A", "TRS-80",
    "TRS-80 CoCo", "TurboGrafx-16", "TurboGrafx-CD", "V.Smile", "Vectrex", "VIC-20", "Virtual Boy", "Watara Supervision", "Wii", "Wii Shop", "Wii U", "Windows Phone", "WonderSwan", "WonderSwan Color", "XaviXPORT",
    "Xbox", "Xbox 360", "Xbox 360 Games Store", "Xbox One", "Zeebo", "Zodiac", "ZX Spectrum"]

#Makes sure that there is a videgames.txt file
if not os.path.isfile("videogames.txt"):
    print "ERROR: NO GAMES FILE PROVIDED "
    exit()

#Gets the start time to count the execution time of the program
startTime = time.time()

#remove files from previous executions, this makes sure that duplicate data is not recorded
if os.path.isfile("Videogames_Found.csv"):
    os.remove("Videogames_Found.csv")
if os.path.isfile("errorlog.csv"):
    os.remove("errorlog.csv")

#Loads the PreferredPlatformArray with the values from the file. The values are stored outside of the application for easier changes and ordering
if os.path.isfile("PlatformList.txt"):
    with open("PlatformList.txt") as inputFile:
        for gameConsole in inputFile:
            preferredPlatformArray.append(gameConsole.rstrip())

#Creates the output files' headers
outputString = ("Title,Release Date,Platform,Suggestion,Notes\n")

#Counts the number of games to process
with open('videogames.txt') as f:
    for game in f:
        numberofGames += 1.0

#Starts the counter at 0
sys.stdout.write("\r0/" + str(int(numberofGames)) + " 0%")

#For each item in the videogames file
with open("videogames.txt") as inputFile:
    #game is the game provided by the user
    for game in inputFile:
        #Try block to prevent any 504 errors
        try:
            #Reset the Values
            platformIndex = 9999
            found = False
            similarity = 0
            newSimilarity = 0

            #Giant Bomb only allows 200 API requests every 15 minutes (800/hour)
            #Waiting 3 seconds will prevent the API key from being locked
            time.sleep(3)

            #Builds the URL to get the queryReplaces all spaces with %20
            getURL = baseURL + string.replace(game, " ", "%20").rstrip() + "'&resources=game&field_list=" + ",".join(feild_list_array)

            #create the downloader object
            opener = urllib2.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]

            #Download and loads the xml
            response = opener.open(getURL).read()

            #Parse the XML
            xmldoc = minidom.parseString(response)

            #For each game in the xml file
            for node in xmldoc.getElementsByTagName('game'):

                #If the xml tag matches the string provided
                if string.replace(str(node.getElementsByTagName("name")[0].firstChild.data).lower().rstrip(), ":", "")== string.replace(str(game).lower().rstrip(), ":", ""):
                    found = True

                #Test the Similarity of the game title provided with the game provided
                else:
                    #Gets the similarity of the current game and the game provided
                    newSimilarity = SequenceMatcher(None, string.replace(str(node.getElementsByTagName("name")[0].firstChild.data).lower().rstrip(), ":", ""), string.replace(str(game).lower().rstrip(), ":", "")).ratio()

                    #if the similarity between the current game is higher than the previous one
                    if similarity < newSimilarity:

                        #Store the new suggestion and the new highest
                        suggestion = str(node.getElementsByTagName("name")[0].firstChild.data).rstrip()
                        similarity = newSimilarity

                        #If the similarity is higher than the threshold consider the games a better match
                        if similarity >= similarityThreshold:
                            found = True
                            similarityFound = True
                            oldGame = game
                            game = suggestion

                #If the game is found
                if (found):
                    succeededGameCount += 1

                    #Get the original release date, which will return an error if it does not exist
                    try:
                        releaseDate = str(node.getElementsByTagName("original_release_date")[0].firstChild.data)[:4]

                    #If there was no original release date try to get the expected
                    except:
                        try:
                            releaseDate = str(node.getElementsByTagName("expected_release_year")[0].firstChild.data)

                        #If the expected release year is not found, list the release year as "N/A"
                        except:
                            releaseDate = "N/A"

                    #Determine the platform
                    minIndex = 9999

                    #for each platform listed for the game
                    for platformname in node.getElementsByTagName('platform'):
                        #Get the index of the most preferred platform
                        minIndex = min(minIndex, preferredPlatformArray.index(platformname.getElementsByTagName('name')[0].firstChild.data))

                    #Gets the platform for the game
                    if minIndex == 9999:
                        foundPlatform = "Not found"
                    else:
                        foundPlatform = preferredPlatformArray[minIndex]

                    #If the game provided was above the similarity threshold write the game to the succeeded file with the old game appended to the end
                    if similarityFound:
                        outputString += (string.replace(str(game.rstrip()), ",", "") + "," + releaseDate + "," + string.replace(foundPlatform, ",", "") + "," + oldGame)

                    #If the game was an exact match write the game to the succeeded file
                    else:
                        outputString += (string.replace(str(game.rstrip()), ",", "") + "," + releaseDate + "," + string.replace(foundPlatform, ",", "") + "\n")
                    break
            #If the game was not found after looping through all the games provided write the game provided to the failed downloads folder
            if not found:
                failedGameCount += 1
                outputString += (str(game.rstrip()) + ",N/A,N/A," + suggestion + ",\"" + getURL + "\"\n")

        #Exits the program immediately if the user presses Ctrl-C or Cmd-C
        except KeyboardInterrupt:
            with open("Videogames_Found.csv", "a") as myfile:
                myfile.write(outputString)
            exit()

        #For all other errors
        except:
            errorCount += 1
            errorString += (str(game.rstrip()) + "," + str(sys.exc_info()[0]) + "\n")

        #Prints out the progress
        progress = ((count/numberofGames)*100)
        sys.stdout.write("\r" + str(count) + "/" + str(int(numberofGames)) + " " + str("{:.2f}".format(progress)) +"%")
        sys.stdout.flush()
        count += 1

        #Resets some more values for the next game
        similarityFound = False
        similarity = 0
        suggestion = "None found"

with open("Videogames_Found.csv", "a") as myfile:
    myfile.write(outputString)
with open("errorlog.csv", "a") as myfile:
    myfile.write(errorString)

#Prints out a summary
print "\n\n----------REPORT----------"
print "Total Game Count: " + str(int(numberofGames))
print "Succeeded Game Count: " + str(succeededGameCount)
print "Failed Game Count: " + str(failedGameCount)
print "Error Count: " + str(errorCount)
print "Run time: %s seconds" %  str("{:.2f}".format(int(time.time() - startTime)))
print "Done"
