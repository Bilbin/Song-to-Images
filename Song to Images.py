import requests
from bs4 import BeautifulSoup
import os
import re
import time
import random

def getImageURL(word):
        """Find all image tags of search result, then get the url for the first one"""
        url = "https://www.google.com/search?q=" + word + "&rlz=1C1CHBF_enUS811US811&source=lnms&tbm=isch&sa=X&ved=0ahUKEwjmovXJ-8jfAhVmmeAKHYiUCcwQ_AUIDigB&biw=1280&bih=648"
        response = requests.get(url)
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        imgTags = soup.find_all("img")
        imgSrc = getImgSrc(imgTags, word)
        if imgSrc == None:
                return None
        print(f"From {imgSrc} ", end = '')
        return imgSrc

def getImgSrc(imgTags, word):
        """Get the source of the image depending on the selected download behavior"""
        tagsLength = len(imgTags)
        #If there are no images
        if tagsLength == 0:
                print(f"No images found for \"{word}\".\n")
                return None
        
        if downloadBehavior == "1":
                index = 0
        elif downloadBehavior == "2":
                #Check if there are less than 5 images
                if tagsLength < 5:
                        index = random.randint(0, tagsLength - 1)
                else:
                        index = random.randint(0, 4)
        elif downloadBehavior == "3":
                #Check if there are less than 10 images
                if tagsLength < 10:
                        index = random.randint(0, tagsLength - 1)
                else:
                        index = random.randint(0, 9)
        elif downloadBehavior == "4":
                index = random.randint(0, tagsLength)
        #Return the source of the selected image
        return imgTags[index]['src']

def download(url):
        """Download the requested image to the requested path"""
        response = requests.get(url)
        fileType = getFileType(response)
        downloadImage(fileType, response)
        

def getFileType(response):
        """Get the file type of the image from the response headers"""
        typeHeader = response.headers['content-type']
        #Find index of slash to get file type
        index = typeHeader.find("/")
        #Get file type using index - excluding everything before the slash
        fileType = typeHeader[index + 1:]
        return fileType

def downloadImage(fileType, response):
        """Open the file and write to it with the image in the response"""
        with open(downloadPath + f"{word}.{fileType}", 'wb') as f:
                print(f'Downloaded image for "{word}".', end = '')
                f.write(response.content)

def getWordList():
        """Get the word list, either through input or a text file"""
        inputChoice = input("Do you want to?\n1. Load the lyrics from a text file\n2. Type/Paste the lyrics here (Note that you cannot have newlines if you do this option. It will error otherwise)\n:")
        while not (inputChoice == "1" or inputChoice == "2"):
                print("Invalid input")
                inputChoice = input("Do you want to?\n1. Load the lyrics from a text file\n2. Type/Paste the lyrics here (Note that you cannot have newlines if you do this option. It will error otherwise)\n:")
        if inputChoice == "1":
                wordList = wordListFromFile()
        elif inputChoice == "2":
                wordList = wordListFromInput()
        #Make all words lowercase
        wordList = [word.lower() for word in wordList]
        #Remove duplicates
        wordList = list(dict.fromkeys(wordList))
        return wordList

def wordListFromInput():
        """Load wordlist from input"""
        wordList = []
        rawLyrics = input("Enter the lyrics here\n:")
        for line in rawLyrics.split("\n"):
                #strip punctuation - as much as possible so as not to miss anything
                strippedLine = re.sub('[!?\[\]\{\}:;"\'/+_|,.*^%$#@]', "", line)
                wordList += strippedLine.split()
        return wordList
                
def wordListFromFile():
        """Load wordlist from file"""
        wordList = []
        fileName = input("What file do you want to load the lyrics from?\n:")
        try:
                with open(fileName, "r") as f:
                        for line in f.readlines():
                                #strip punctuation - as much as possible so as not to miss anything
                                strippedLine = re.sub('[!?\[\]\{\}:;"\'/+_|,.*^%$#@]', "", line)
                                wordList += strippedLine.split()
        except FileNotFoundError:
                raise Exception("That file does not exist.")
        return wordList

def getDownloadPath():
        """Get the selected download path for the images"""
        path = input("What folder do you want to download the images to?\n:")
        if os.path.isfile(path):
                raise Exception("That is a file, not a folder.")
        if not os.path.exists(path):
                raise Exception("That folder does not exist.")
        #Add a slash at the end if there is not one, to indicate that it is a directory
        if not path[-1] == "/":
                path += "/"
        return path

def getDownloadBehavior():
        """Get the download behavior of the program - which images are downloaded"""
        behaviorChoice = input("Do you want to?\n1. Get the first image from the google search\n2. Get a random image from the first five image results\n3. Get a random image from the first ten image results\n4. Get a random image from all available images (on the first results page)\n:")
        while not (behaviorChoice == "1" or behaviorChoice == "2" or behaviorChoice == "3" or behaviorChoice == "4"):
                print("Invalid input")
                behaviorChoice = input("Do you want to?\n1. Get the first image from the google search\n2. Get a random image from the first five image results\n3. Get a random image from the first ten image results\n4. Get a random image from all available images (on the first results page)\n:")
        return behaviorChoice

#Start a timer to show how much time it took at the end
startTime = time.time()
#Counter for showing successfully downloaded images
downloadedImages = 0
wordList = getWordList()
downloadPath = getDownloadPath()
downloadBehavior = getDownloadBehavior()
#Word counter for percentage
wordCounter = 1
print(f"\nStarting to download {len(wordList)} image(s).\n")
for word in wordList:
        url = getImageURL(word)
        if url == None:
                #Continue if no images were available
                continue
        download(url)
        downloadedImages += 1
        percentDone = str(round((wordCounter / len(wordList)) * 100))
        print(f" ({percentDone}% Done)\n")
        wordCounter += 1

#Get and print elapsed time of the program
endTime = time.time()
elapsedTime = str(round(endTime - startTime))
print(f"Successfully downloaded {str(downloadedImages)} image(s) in {elapsedTime} seconds.")
