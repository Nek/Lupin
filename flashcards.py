import datetime
import pickle
from hashlib import md5
from os import path

import sm2

from random import randint

from config import getflashcardsTag
import utils

class Flashcard:

    def __init__(self, question, answer, source): 
        self.question = question
        self.answer   = answer
        self.source   = source
        
        
        self.next = datetime.datetime(2021, 1, 1).timestamp()
        self.lastAnswered = datetime.datetime(2021, 1, 1).timestamp()
        self.history = []
    
    def __repr__(self): 
        a = [self.question, self.answer, self.next, self.source, self.history]
        return str(a) #"[% s ][% s]" % (self.question, self.answer)  

    def updateProperties(self, next, history):
        self.next = next
        self.history = history

SEPARATOR = "#"
flashcardsDB = "flashcards.db"

def scan4Flashcards(content):
    Qlist = []
    buildFlashcardList(content, Qlist)
    return (Qlist)

def countIdent(line): # TODO change that to .index and merge with utils function
    count = 0
    if(len(line) > 0):
        while line[count] == SEPARATOR:
            if(count == len(line) - 1):
                break
            count += 1    
    return count

def buildFlashcardList(content, Qlist):
    lines = content.split('\n')
    i = 0
    source = ""
    while i <= len(lines) - 1:
        if 'title:' in (lines[i]).lower():
            source = lines[i].strip()
        if getflashcardsTag() in lines[i]:
            flashcardIndent = countIdent(lines[i])
            isSub = True
            i += 1
            flashcard = Flashcard("-1", "-1", source)
            while isSub:
                if( i == len(lines)):
                    break

                currentIdent = countIdent(lines[i])
                if(currentIdent == flashcardIndent + 1):
                    if(flashcard.question != "-1"):
                            Qlist.append(flashcard)
                    flashcard = Flashcard("-1", "-1", source)
                    flashcard.question = lines[i][currentIdent:].strip()
                    i += 1
                elif(currentIdent > flashcardIndent + 1):  # scan for answer
                    blockRef = utils.containsRefBlock(lines[i])
                    answer = ""
                    if (blockRef):
                        origLine = (lines[i][currentIdent:]).replace("(("+blockRef+"))","").strip()
                        if(origLine):
                            answer = origLine + " "
                        answer += utils.findOrigBlock(blockRef)
                    else:
                        answer = lines[i][currentIdent:]
                    if(flashcard.answer == "-1"):
                        flashcard.answer = ""
                    flashcard.answer += answer.strip() + "\n"
                    i += 1                
                else:
                    isSub = False
                    i -= 1
            if(flashcard.answer != "-1"):
                Qlist.append(flashcard)
        i += 1

def saveFlashcardsDB(flashcardList, dump=False):
    if(dump): # don't check for differences 
        with open(flashcardsDB, "wb") as fp:   # Pickling
            pickle.dump(flashcardList, fp) 
        print (str(len(flashcardList)) + " cards saved")
    elif(not(path.exists(flashcardsDB))): # new DB
        with open(flashcardsDB, "wb") as fp:   # Pickling
            pickle.dump(flashcardList, fp)
        return [str(len(flashcardList)), "0" ]     
    else: # updating exsiting DB
        savedDB = loadFlashcardsDB()
        tmpset = set((x.question) for x in savedDB)
        newFlashcards = [ x for x in flashcardList if (x.question) not in tmpset ]
        tmpset = set((x.question, x.answer) for x in savedDB)
        updatedFlashcards = [ x for x in flashcardList if ((x.question, x.answer) not in tmpset and x not in newFlashcards)]
        if updatedFlashcards: # no need to check for new since they will be saved with the updated ones (if any)
            for updatedFlashcard in updatedFlashcards:
                cardDetails = getFlashcardDetails(updatedFlashcard.question, savedDB)
                cardIndex = flashcardList.index(updatedFlashcard)
                print(cardDetails.index)
                flashcardList[cardIndex].updateProperties(cardDetails[0].next, cardDetails[0].history)
                print(flashcardList[cardIndex])
            # print(updatedAnswers)
            saveFlashcardsDB(flashcardList, True)
        elif newFlashcards:
            savedDB += newFlashcards
            saveFlashcardsDB(savedDB, True)
            print(newFlashcards)

        return [str(len(newFlashcards)), str(len(updatedFlashcards)) ]
      
def loadFlashcardsDB():
    with open(flashcardsDB, "rb") as fp:   # Unpickling
        db = pickle.load(fp)
    return db

def getFlashcardDetails(question, flashcardList = ""):
    if (not(flashcardList)):
        flashcardList = loadFlashcardsDB() # in saved DB
    #print (flashcardList[0])
    return [x for x in flashcardList if x.question == question]

def updateFlashcard(flaschard):
    flashcardsDB = loadFlashcardsDB()
    flaschard.lastAnswered = (datetime.datetime.now()).timestamp()
    flaschard.next = flaschard.lastAnswered +  sm2.supermemo_2(flaschard.history) * 86400
    cardIndex = next(i for i, x in enumerate(flashcardsDB) if x.question == flaschard.question)
    print(flashcardsDB[cardIndex])
    print(datetime.datetime.fromtimestamp(flashcardsDB[cardIndex].next) )
    flashcardsDB[cardIndex] = flaschard
    print(flashcardsDB[cardIndex])
    print(datetime.datetime.fromtimestamp(flashcardsDB[cardIndex].next) )
    saveFlashcardsDB(flashcardsDB, True)
    
    return datetime.datetime.fromtimestamp(flaschard.next).strftime("%Y-%m-%d") 

def getFlashcardFromPool():
    flashcardsList = loadFlashcardsDB()
    tsToday = (datetime.datetime.now()).timestamp()
    overdueFC =  [ x for x in flashcardsList if (x.next) <= tsToday ] # get overdue FC
    if overdueFC:
        return(overdueFC[randint(0,len(overdueFC)-1)])
    else:
        return None


