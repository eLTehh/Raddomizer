from binascii import hexlify, unhexlify
import random
import json
from distutils.dir_util import copy_tree

#from this import s 
from fe12LZ77 import fe12_compress, fe12_decompress
import os 

import logging 

class dataEditor:

    def __init__(self, directory):

        self.status = ""

        self.directory = directory 

        logging.basicConfig(filename=directory + "\\error.log", level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

        self.logger = logging.getLogger(__name__)

        self.randomCharacters = True 
        self.randomGrowths = True 
        self.randomBases = True 
        self.randomClasses = True 

        self.removeWepLocks = True 
        self.abolishGender = True 

        self.enableManaketes = True 
        self.enableBallistas = True 

        self.absoluteBases = False 
        self.absoluteGrowths = False 

        self.growthsRange = [0, 100]

        self.replacementDict = {}
        self.maxDancerCount = 1  
        self.currentDancerCount = 0
        self.maxFreelanceCount = 1
        self.currentFreelanceCount = 0

        self.logDict = {}
        self.chapterLogDict = {}

        self.growthToHexDict = json.load(open(self.directory + "\\randomizer_info\\fe12cyphers.json","r"))
        self.hexToGrowthDict = json.load(open(self.directory + "\\randomizer_info\\fe12cyphersR.json","r"))
        self.ogDataDict = json.load(open(self.directory + "\\randomizer_info\\fe12ogData.json"))
        self.nameList = open(self.directory + "\\randomizer_info\\Character List.txt", 'r').read().split('\n')
        self.classDict = json.load(open(self.directory + "\\randomizer_info\\fe12classes.json"))
        self.disposDict = json.load(open(self.directory + "\\randomizer_info\\disposPointers.json"))

        self.slotList = open(self.directory + "\\randomizer_info\\internalChapterList.txt").read().split('\n')
        self.chapterDict = json.load(open(self.directory+"\\randomizer_info\\chaptersInOrder.json"))
        
        self.itemDict = json.load(open(self.directory+ "\\randomizer_info\\fe12items.json"))
        self.itemToGroup = json.load(open(self.directory + "\\randomizer_info\\itemToGroup.json"))
        self.groupToItem = json.load(open(self.directory + "\\randomizer_info\\groupToItem.json"))

    def getSettings(self):
        settingsDict = {
            "Random Growths": self.randomGrowths,
            "Random Bases": self.randomBases,
            "Random Classes": self.randomClasses,
            "Random Portraits": self.randomCharacters,

            "Growths Range": self.growthsRange,

            "Enable Manaketes": self.enableManaketes,
            "Enable Ballisticians": self.enableBallistas ,

            "Absolute Bases": self.absoluteBases,
            "Absolute Growths": self.absoluteGrowths,

            "Max Dancer Count": self.maxDancerCount,
            "Max Freelancer Count": self.maxFreelanceCount
        }

        return settingsDict 

    def addMiscGraphics(self, output):
        if self.enableBallistas:
            #Adds ballista sprites into the game
            copy_tree(self.directory+"\\randomizer_info\\ballista\\", output)

###Randomizer functions begin here. 


    def randomClassHelper(self, seed):
        random.seed(seed)
        self.currentDancerCount = 0

        classBlacklist = ["Soldier", "Barbarian", "Pegasus Knight", "Emperor", "Magic Dragon",
                        "Earth Dragon", "Fire Dragon", "Ice Dragon", "Knight F",
                        "Wyvern", "Divine Dragon", "Dark Dragon"]

        if not self.enableManaketes:
            classBlacklist.append("Manakete")

        if not self.enableBallistas:
            classBlacklist.append("Ballistician")

        if self.randomClasses == True:
            for i in range(77):
                cName=  self.nameList[i]
                if cName != "Avatar":
                    self.logDict[cName] = {}
                    
                    ogTier = self.ogDataDict[cName]["Tier"]
                    newTier = None

                    classList = [i for i in list(self.classDict) \
                        if i not in classBlacklist]

                    while True:
                        self.logDict[cName]["Class"] =  random.choice(classList)
                        newTier = self.classDict[self.logDict[cName]["Class"]]["Tier"]

                        if self.logDict[cName]["Class"] == "Dancer" and self.maxDancerCount!= -1:
                            if self.currentDancerCount == self.maxDancerCount:
                                continue 
                            else:
                                self.currentDancerCount+=1
                                break

                        if self.logDict[cName]["Class"] == "Chameleon" and self.maxFreelanceCount != -1:
                            if self.currentFreelanceCount == self.maxFreelanceCount:
                                continue 
                            else:
                                self.currentFreelanceCount+=1
                                break

                        if ogTier == newTier or newTier == "-":
                            break
        



    def randomize(self, input_path, output_path, seed = None):
        try:
            #create output if doesn't exist
            if not os.path.exists(output_path+'\\data'):
                os.makedirs(output_path+'\\data')

            if not os.path.exists(output_path+'\\dispos'):
                os.makedirs(output_path+'\\dispos')

            if os.path.exists(input_path+"\\data\\data"):
                input_path+= "\\data"

            #print(input_path+"\\dispos\\")
            if not os.path.exists(input_path+"\\dispos\\"):
                return "Error"
            
            if seed == None:
                seed = random.randint(-2147483647, 2147483647)




            #GDinput = bytearray(open(input_path+'\\data\\data\\FE12data.bin.rdcmp', 'rb').read())    
            #GDoutput = open(output_path+'\\data\\FE12data.bin.rdcmp', 'wb')

            self.randomClassHelper(seed)

            #print(self.logDict)
            #print(self.rClassDict)
            if self.randomGrowths or self.randomBases or self.randomClasses or self.randomCharacters:
                self.randomizeGameData(input_path+'\\data', seed, output_path +'\\data')

            #GDoutput.write(GDinput)
            #GDoutput.close() #merge output writing into gamedata function

            if self.randomClasses:
                self.randomizeDispos(input_path+"\\dispos", seed, output_path+'\\dispos')

            self.addMiscGraphics(output_path)

            self.randomizeScript(input_path+"\\m", seed, output_path + '\\m')

            self.status = " Randomization success! \n Please drag the data folder from the output back into  \n your unpacked directory and re-pack your ROM. \n\n (Make a copy for backup, just in case.)"

            self.writeLog(seed, output_path)


            return "helyea"

        except Exception as e:
            self.status = "Error"
            self.logger.exception("Exception on randomizer")
            #raise
            





    
    def randomizeGameData(self, input_path, seed, output_path):
        print("Writing FE12data...")
        print("Decompressing...")

        self.status = "Decompressing FE12data..."
        fe12_decompress(input_path+'\\FE12data.bin', input_path+'\\FE12data.bin.decmp')
        input = bytearray(open(input_path+'\\FE12data.bin.decmp', 'rb').read())

        
        print("Decompression complete, writing data...")

        self.status = "Decompression complete, writing data..."


        random.seed(seed)
        

        #chardata starts at 32
        #logData = "Seed: " + str(seed) + "\n"
        characterList = [self.nameList[0]] + self.nameList[2:77]


        for charIndex in range(77):

            self.status = "Characters " + str(charIndex+1) + "/77 complete..."

            cName = self.nameList[charIndex]
            startingPointer = charIndex*92 + 32
            
            if cName not in self.logDict:
                self.logDict[cName] = {}

            if self.randomCharacters:
                if cName != "Avatar": #repoint pid to someone else's
                    if cName == "Marth" and "play ghost trick" in seed.lower():
                        randomizedChar = "Radd"
                    else:
                        randomizedChar = random.choice(characterList)
                    characterList.remove(randomizedChar)

                    #logData += "Replaced with: " + randomizedChar + '\n' 
                    self.logDict[cName]["Replacement"] = randomizedChar 

                    newPID = self.ogDataDict[randomizedChar]["FID"]
                    for i in range(4):
                        input[startingPointer+ 4 + i] = newPID[i]

                    self.replacementDict[cName] = randomizedChar
                


            #logData+= "Stats:\nHP/Str/Mag/Skl/Spd/Lck/Def/Res\n"

            #print(cName + "bases")
            if self.randomBases:
                #roll random base stats
                basesTotal = self.ogDataDict[cName]["Bases"]["Total"]
                newBases = []
                basesRange = self.ogDataDict[cName]["Bases"]["Range"]

                while True:
                    newBases = []
                    for i in range(8):
                        base = random.randrange(basesRange[0], basesRange[1])
                        if base < 0: #signed integer moment
                            base+= 256
                        newBases.append(base)
                    if sum(newBases) == basesTotal and not self.absoluteBases:
                        break
                    if self.absoluteBases:
                        break 
                
                #if tiki or bantu not manakete, add in their dragonstone bonuses
                dstoneBonuses = {
                    "Tiki": [0, 10, 0, 7, 4, 0, 15, 11],
                    "Bantu": [0, 8, 0, 4, 4, 0, 9, 4]
                }

                if (cName == "Tiki" or cName == "Bantu") \
                    and (self.logDict[cName]["Class"] != "Manakete" or\
                        self.logDict[cName]["Class"]!= "Manakete (F)"):
                    for i in range(8):
                        newBases[i] += dstoneBonuses[cName][i]


                self.logDict[cName]["Bases"] = newBases
                
                #logData+= "Bases: " + '/'.join([str(i) for i in newBases]) +'\n'

                #write random base stats
                for i in range(8):
                    input[startingPointer + 12 + i] = newBases[i]

            #print(cName + "growths")                
            if self.randomGrowths:

                #roll random growths 
                growthsTotal = self.ogDataDict[cName]["Growths"]["Total"]
                newGrowths = []
                growthsRange = [self.growthsRange[0], self.growthsRange[1]] #maybe this can be modified depending on user input

                maxGrowthsTotal = growthsRange[1] * 8 #if your upper limit is something wacky like 0



                if not self.absoluteGrowths:
                    if cName == "Bantu":
                        growthsRange[0] = -20
                    if cName == "Arran" and growthsRange[1] > 10:
                        growthsRange[1] = 10
                        if growthsRange[0] == 10:
                            growthsRange[0] = 0

                    #edge case: min growths > character bst 
                    #like...arran...

                    if growthsRange[0] > growthsTotal:
                        growthsRange[0] = 0
                


                count = 0
                while True:
                    #print(cName)
                    newGrowths = []
                    #print(newGrowths)
                    for i in range(8):

                        growth = random.randrange(growthsRange[0], growthsRange[1], 5)
                        if growth > 80:
                            growth = growth - growth%10
                        newGrowths.append(growth)
                    if growthsTotal < maxGrowthsTotal:
                        count +=1 
                    
                    if count == 10000:
                        break
                    if (sum(newGrowths) == min(maxGrowthsTotal, growthsTotal)) and not self.absoluteGrowths:
                        break
                    if self.absoluteGrowths or growthsRange[1] < 0:
                        break 
                
                #logData+= "Growths: " + '/'.join([str(i) for i in newGrowths]) +'\n'
                self.logDict[cName]["Growths"] = newGrowths

                #write random base stats
                statsName = 'HP Str Mag Skl Spd Lck Def Res'.split()

                for i in range(8):
                    actualGrowth = int(self.growthToHexDict[cName][statsName[i]][str(newGrowths[i])], 16)
                    input[startingPointer + 20 + i] = actualGrowth

            #logData+= "\n"
            if self.randomClasses:


                    if cName!= "Avatar":

                        #falco check
                        if self.logDict[cName]["Class"] == "Falcon Knight":
                            input[startingPointer + 47] = 197


                        wRankPointers = {
                            "Sword": 36,
                            "Lance": 37,
                            "Axe": 38,
                            "Bow": 39,
                            "Magic": 40,
                            "Staff": 41
                        }

                        #Check character's current weapon rank. 
                        #Sort list of which wepranks are prioritized (numbers only, ignore 0)
                        wRankNumeric = []
                        for wep in self.ogDataDict[cName]["Weapon Ranks"]:
                            rPoints = self.ogDataDict[cName]["Weapon Ranks"][wep]
                            wRankNumeric.append(rPoints)

                        wRankNumeric.sort(reverse = True) #descending order


                        #Check character's class
                        #Sort class weapon ranks (Name)

                        wRankTypes = []

                        charClass = self.logDict[cName]["Class"]
                        for wep in self.classDict[charClass]["Weapon Ranks"]:
                            wRankTypes.append(wep)

                        wRankTypes.sort(key = lambda x:self.classDict[charClass]["Weapon Ranks"][x], reverse = True)
                        self.logDict[cName]["Weapon Ranks"] = {}

                        for i in range(len(wRankTypes)):
                            #possible edge case where more than original class

                            newWrank = wRankNumeric[i]


                            self.logDict[cName]["Weapon Ranks"][wRankTypes[i]] = newWrank



                            wrPointer = wRankPointers[wRankTypes[i]]

                            input[startingPointer + wrPointer] = newWrank #updating weapon ranks in game



                    #update weapon rank according to class wrank prioriity
                
        
        #Class Slots
        #Keep Class slot dict of class slot additions
        if self.randomClasses:
            self.state = "Generating class slots..."
            classSlotAdditions = {
                "Flier": 0,
                "Cavalier": 0,
                "Knight": 0,
                "Archer": 0,
                "Mercenary":0,
                "Myrmidon": 0,
                "Fighter": 0,
                "Hunter": 0,
                "Pirate": 0,
                "Dark Mage": 0,
                "Mage": 0,
                "Cleric": 0
            }


            #For chapter in chapter
            for chapterIndex in range(len(self.chapterDict)):


                chapter = list(self.chapterDict.keys())[chapterIndex]
                self.chapterLogDict[chapter] = {}
                self.state = "Calculating class slots for " + chapter + "..."
                print(self.state)
                for cName in self.chapterDict[chapter]:

                    if cName != "Avatar":
                        #For character in chapter
                        charClass = self.logDict[cName]["Class"]
                        classSlot = self.classDict[charClass]["Class Slot"]
                        if classSlot != 'None':
                            classSlotAdditions[classSlot]+=1

                            #Get class
                            #Get class slot associated with class
                            #Class slot +=1
                    #cSlotPointer = 56476+chapterIndex*44

                for cSlotIndex in range(12):
                    slotKey = list(classSlotAdditions.keys())[cSlotIndex]

                    totalSlots = classSlotAdditions[slotKey] + 1

                    #input[cSlotPointer + cSlotIndex] = totalSlots 

                    self.chapterLogDict[chapter][slotKey]  = totalSlots 

                #Then for the chapter, read existing class slots (use the dict)
                #Add the additions from the dict
                #???
                #Profit :)

            for chapterIndex in range(len(self.slotList)): #in-game chapter order 
                chapter = self.slotList[chapterIndex]
                self.state = "Generating class slots for " + chapter + "..."

                for cSlotIndex in range(12):
                    slotKey = list(classSlotAdditions.keys())[cSlotIndex]
                    totalSlots = self.chapterLogDict[chapter][slotKey]
                    cSlotPointer = 56476+chapterIndex*44
                    input[cSlotPointer + cSlotIndex] = totalSlots 
                       
                

            

        if self.removeWepLocks:
            #Remove weapon locks for Falchion, Wing Spear, Rapier, hammerne and Aum
            #items start at 0xA308, 60 bytes long 

            #Naming these nicely so I can keep track of what the heck's going on
            #instead of using a loop like a normal person

            startingPointer = 41736

            #Rapier 0x0B, Ability 7
            rapierPointer = startingPointer + 60*11 + 42
            input[rapierPointer] = 0

            #Falchion 0x0E, Ability 7
            falPointer = startingPointer + 60*14 + 42
            input[falPointer] = 0

            #Wing Spear 0x17, Ability 7
            wspearPointer = startingPointer + 60*23 + 42
            input[wspearPointer] = 0

            #Hammerne 0x47, Ability 7
            hammPointer = startingPointer + 60*87 + 42
            input[hammPointer] = 0

            #Aum 0x5A, Ability 7
            aumPointer = startingPointer + 60*90 + 42
            input[aumPointer] = 0

        if self.abolishGender: #NON-SEXIST WEAPONS GO
            #Ladyblade 0x0F, Ability 8
            lbladePointer = startingPointer + 60*15 + 43
            input[lbladePointer] = 0

            #Aura 0x38, Ability 8
            auraPointer = startingPointer + 60*56 + 43
            input[auraPointer] = 64 #0x40 - cannot be forged

            #Excalibur 0x39, Ability 8
            excaliburPointer = startingPointer + 60*57+ 43
            input[excaliburPointer] = 64 #0x40 - cannot be forged

            #Divinestone 0x45, Ability 8
            dstonePointer = startingPointer + 60*69 + 43
            input[dstonePointer] = 64 #0x40 cannot be forged




        #print("Success!")
        #logFile = open("C:\\Users\\lt123\\stoof\\coding\\fe12 randomizer\\randomizerLog.txt", "w")
        #logFile.write(logData)
        #logFile.close()

        decmp = open(input_path+'\\FE12data.bin.decmp', "wb")
        decmp.write(input)
        decmp.close()

        self.status = "Recompressing FE12data..."
        print("Recompressing FE12data...")

        if not os.path.exists(output_path):
            os.makedirs(output_path)



        fe12_compress(input_path+'\\FE12data.bin.decmp', output_path+'\\FE12Data.bin')

        os.remove(input_path+"\\FE12data.bin.decmp")

        print("FE12data written!")
        self.status = "FE12data written!"

        return input

    def randomizeDispos(self, input_path, seed, output_path):
        print("Randomizing Dispos...")
        self.status = "Randomizing Dispos..."
        random.seed(seed)
        #Add join maps + hex positions to character dictionary

        #Call it in this function!

        #generate dict of characters and their respective randomized classes
        #write this to log as well


        mapList = "202 203 204 205 206 207 208 103 106 110 113 116 001 002 003 004 005 006 007 008 009 010 011 012 013 014 015 016 017 019 020 021 022 024".split()
        mapList = ["bmap"+ i for i in mapList]

        for map in mapList:
            print("Randomizing " + map + "...")

            self.status = "Randomizing " + map + "..."
            #iterate through each map
            #read map, decompress
            mapPath = input_path + "\\" + map 
            fe12_decompress(mapPath, mapPath+'.decmp')
            input = bytearray(open(mapPath+'.decmp', 'rb').read())




            mapData = self.disposDict[map]

            groupWepRanks = {
                "Iron": 0,
                "Ranged": 30,
                "Devil": 30,
                "Steel": 30,
                "Killer": 75,
                "Silver": 105,
            }

            #iterate through each character
            for cName in mapData:
                if cName not in ["Bantu", "Est", "Midia"] or self.logDict[cName]["Class"] != "Chameleon":
                    inventoryIterated = False 
                    for pointer in mapData[cName]: #Thanks cecil now I have to iterate through pointers :/
                        #pointer = mapData[cName]


                        newClass = self.logDict[cName]["Class"]
                        #class pointer at input[pointer+3]
                        #Change class
                        input[pointer+3] = self.classDict[newClass]["Dispos Pointer"]

                        weaponChanged = False 

                        #Check weapon rank of new class...

                        if "Inventory" in self.logDict[cName] and not inventoryIterated and cName != "Rickard":
                            self.logDict[cName]["Inventory2"] = {}

                        else:
                            self.logDict[cName]["Inventory"] = {}

                        inventoryIterated = True 


                        

                        for i in range(4):

                            wPointer =  [17, 21, 25, 29][i]
                            oldWep = input[pointer+wPointer]
                            maxWepRank = max(self.logDict[cName]["Weapon Ranks"].values())
                            #print(cName)
                            #print(pointer)
                            #print(maxWepRank)

                            if str(oldWep) in self.itemToGroup:
                                #print("Changing...")
                                #print(cName)
                                weaponChanged = True 
                                #print(cName + "Yes")
                                if self.logDict[cName]["Class"]  == "Manakete":
                                    input[pointer + wPointer] = random.randint(66,69)

                                elif self.logDict[cName]["Class"] == "Manakete (F)":
                                    input[pointer + wPointer] = 70
                                    
                                elif self.logDict[cName]["Class"] == "Ballistician":
                                    input[pointer + wPointer] = random.randint(61, 65)

                                else:

                                    wGroup = self.itemToGroup[str(oldWep)]["Group"]
                                    
                                    #print(wGroup)

                                    if wGroup in ["Devil", "Ranged"] and \
                                    self.logDict[cName]["Weapon Ranks"]["Sword"] < 30\
                                    and self.logDict[cName]["Weapon Ranks"]["Axe"]<30:
                                        #If not enough weapon rank
                                        if maxWepRank == 30:
                                            wGroup = "Steel"
                                        else:
                                            wGroup = "Iron"
                                        


                                    #Get new weapon
                                    minWrank = groupWepRanks[wGroup]

                                    newWep = ""

                                    for wep in self.logDict[cName]["Weapon Ranks"]:
                                        #IF weapon rank > min weapon rank
                                        if self.logDict[cName]["Weapon Ranks"][wep] >= minWrank:
                                            newWep = self.groupToItem[wGroup][wep]["Pointer"]
                                            #Get new weapon
                                            break
                                    #print(newWep)
                                    #Write new weapon into game 
                                    if newWep != "" and newWep!=None:
                                        
                                        input[pointer+ wPointer] = newWep
                                    else:
                                        weaponChanged = False 

                            #if no weapons have been changed
                            if (weaponChanged == False and oldWep == 0) or\
                                (weaponChanged == False and i == 3): #Last one is to account for Athena...

                                if cName == "Est" or cName == "Bantu" or cName == "Midia":
                                    #Ignore these, they don't have inventories
                                    pass 

                                elif self.logDict[cName]["Class"] == "Manakete":
                                    input[pointer + wPointer] = random.randint(66,69)
                                    weaponChanged = True 

                                elif self.logDict[cName]["Class"] == "Manakete (F)":
                                    input[pointer + wPointer] = 70
                                    weaponChanged = True    

                                elif self.logDict[cName]["Class"] == "Ballistician":
                                    input[pointer + wPointer] = random.randint(61, 65)
                                    weaponChanged = True
                                #add one that fits the wep rank

                                else:
                                    #print(cName)
                                    wGroup = None
                                    for group in groupWepRanks:
                                        if groupWepRanks[group] <= maxWepRank:
                                            wGroup = group

                                    minWrank = groupWepRanks[wGroup]

                                    newWep = ""

                                    for wep in self.logDict[cName]["Weapon Ranks"]:
                                        #IF weapon rank > min weapon rank
                                        if self.logDict[cName]["Weapon Ranks"][wep] >= minWrank:
                                            newWep = self.groupToItem[wGroup][wep]["Pointer"]
                                            #Get new weapon
                                            break

                                    if newWep != "":
                                        input[pointer+ wPointer] = newWep
                                        weaponChanged = True 

                                

                                #Weapon rank documentation:
                                '''
                                0 - E
                                30 - D
                                40 - D lv2
                                45 - D lv3
                                75 - C
                                105 - B
                                135 - B lv2
                                165 - A
                                195 - A lv2
                                '''

                            if "Inventory2" in self.logDict[cName]:
                                self.logDict[cName]["Inventory2"][i] = self.itemDict[str(input[pointer+wPointer])]
                            else:
                                self.logDict[cName]["Inventory"][i] = self.itemDict[str(input[pointer+wPointer])]



            #write map, compress again
            newInput = open(mapPath+'.decmp', 'wb')
            newInput.write(input)
            newInput.close()

            if not os.path.exists(output_path):
                os.makedirs(output_path)


            fe12_compress(mapPath+'.decmp', output_path + "\\" + map)

            os.remove(mapPath+'.decmp')




        print("Dispos randomized!")
        self.status = "Dispos randomized!"

        return input_path
    
    def randomizeScript(self, input_directory, seed, output_directory):
        #add pointers later
        pass
        '''
        random.seed(seed)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        input_directory = input_directory

        #print(self.replacementDict)


        #change this into a loop later

        fe12_decompress(input_directory+"\\001", output_directory+"\\001.decmp")
        newScript = open(output_directory+"\\001.decmp", 'rb').read()

        dontCallAgain = []

        for ogChar in self.replacementDict:
            if ogChar not in dontCallAgain:
                replacement = self.replacementDict[ogChar]
                dontCallAgain.append(replacement) #so we won't go through a long string of replacing the same guy

                ogChar = ogChar

                ogPortrait = str.encode(self.ogDataDict[ogChar]["Script ID"] + "|")
                replacementPortrait = str.encode(self.ogDataDict[replacement]["Script ID"] + "|")

                replacement = str.encode(replacement)
                ogChar = str.encode(ogChar)

                newScript = replacementPortrait.join(newScript.split(ogPortrait))
                newScript = replacement.join(newScript.split(ogChar))


        #print(str.encode("YMIR|").join(newScript.split(str.encode("MARS|"))))

        finalScript= open(output_directory+"\\001.decmp", 'wb')
        finalScript.write(newScript)
        finalScript.close()
        fe12_compress(output_directory+"\\001.decmp", output_directory+"\\001")
        os.remove(output_directory+"\\001.decmp")
        '''

    def writeLog(self, seed, output_path):
        logData = "Seed: " + str(seed) 

        for setting in self.getSettings():
            if setting == "Growths Range":
                logData += "\n" + setting + ": " + str(self.getSettings()[setting][0]) + "% - " + str(self.getSettings()[setting][1]) + "%"

            else:
                logData += "\n" + setting + ": " + str(self.getSettings()[setting])

        if self.randomBases or self.randomGrowths:
            logData+="\n\nAll bases/growths shown below are BEFORE class bonuses."
            logData+="\nYou may find a list of class bonuses here:"
            logData+="\nhttps://serenesforest.net/light-and-shadow/classes/base-stats/"
            logData+="\nhttps://serenesforest.net/light-and-shadow/classes/growth-rates/player/"


        if self.randomCharacters:
            logData += "\n\nRecruitments:"

            recruitPairs = {
                "Warren": "Catria",
                "Matthis": "Julian",
                "Sirius": "Ogma",
                "Barst": ["Cord", "Bord", "Ogma"],
                "Samto": ["Ogma", "Caeda"],
                "Roger": "Caeda",
                "Etzel": "Marth",
                "Elrean": "Wendell",
                "Jake":"Caeda",
                "Daross": "Marth",
                "Beck": "Marth",
                "Tiki": "Marth",
                "Abel": ["Marth", "Est"],
                "Astram": "Jeorge",
                "Sheena": "Marth",
                "Samson": "Sheena",
                "Sedgar": "Vyland", 
                "Wolf": "Sedgar",
                "Lena": "Julian",
                "Nyna": "Sirius",
                "Maria": "Minerva",
                "Elice": "Merric"
            }

            logData +="\n"

            for key in recruitPairs:
                if type(recruitPairs[key]) == list:
                    logData += "\nTalk to " + self.logDict[key]["Replacement"] + " with " +\
                         ", ".join([self.logDict[i]["Replacement"] for i in recruitPairs[key]])
                else:
                    logData += "\nTalk to " + self.logDict[key]["Replacement"] + " with " + self.logDict[recruitPairs[key]]["Replacement"]

        for character in self.logDict:
            logData+= "\n\n" + character 

            for value in self.logDict[character]:
                toWrite = self.logDict[character][value]

                if type(toWrite) == list:
                    logData+="\n" + value + ": "
                    stats = "HP STR MAG SKL SPD LCK DEF RES".split()
                    for index in range(len(toWrite)):
                        logData += stats[index] + " " + str(toWrite[index])
                        if value == "Growths":
                            logData += "%"
                        logData+= " "

                else:
                    name = value 
                    if "Inventory2" in self.logDict[character] and value == "Inventory":
                        name = "Prologue Inventory"
                    if value == "Inventory2":
                        name = "Inventory"

                    logData+="\n" + name + ": " + str(self.logDict[character][value])

        logData += "\n\nClass Slots:"
        for chapter in self.chapterLogDict:
            logData+= "\n\n"+chapter +"---"

            for slot in self.chapterLogDict[chapter]:
                logData+="\n"+slot+ ": " + str(self.chapterLogDict[chapter][slot])

        
        #localize names from internal code
        nameReplacements = {
            "Rody":"Roderick",
            "Yubello":"Jubelo",
            "Yumina":"Yuliya",
            "Feena":"Phina",
            "Daross":"Darros",
            "Robert":"Roberto",
            "Leiden":"Reiden",
            "Elrean":"Arlen",
            "Samuel":"Samto",
            "Chameleon":"Freelancer"
        }

        for oldName in nameReplacements:
            logData = nameReplacements[oldName].join(logData.split(oldName))
            
        outputFileName = "\\randomizerLog" + seed + ".txt"
        log = open(self.directory+outputFileName, "w")
        log = open(output_path.split("\\output")[0]+outputFileName, "w")

        log.write(logData)
        log.close()





        
        


