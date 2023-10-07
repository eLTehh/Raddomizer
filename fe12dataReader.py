#from binascii import hexlify, unhexlify
import random
import json
import comp
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
        self.randomItems = True
        self.randomEnemies = True

        self.removeWepLocks = True 
        self.abolishGender = True 

        self.enableManaketes = True 
        self.enableBallistas = True 

        self.absoluteBases = False 
        self.absoluteGrowths = False
        
        self.mixLandFlying = False
        self.mixHumanDragon = True
        
        self.noPrologue = False

        self.growthsRange = [0, 100]

        self.itemPowerRange = 4
        self.itemHitRange = 20
        self.itemUsesRange = 15
        self.itemCritChance = 5
        self.itemCritRange = [10,40]

        self.replacementDict = {}
        self.maxDancerCount = 1  
        self.currentDancerCount = 0
        self.maxFreelanceCount = 1
        self.currentFreelanceCount = 0

        self.logDict = {}
        self.chapterLogDict = {}
        self.itemLogDict = {}

        self.growthToHexDict = json.load(open(self.directory + "\\randomizer_info\\fe12cyphers.json","r"))
        self.hexToGrowthDict = json.load(open(self.directory + "\\randomizer_info\\fe12cyphersR.json","r"))
        self.ogDataDict = json.load(open(self.directory + "\\randomizer_info\\fe12ogData.json"))
        self.buffDataDict = json.load(open(self.directory + "\\randomizer_info\\prologueSkipUnits.json"))
        self.nameList = open(self.directory + "\\randomizer_info\\Character List.txt", 'r').read().split('\n')
        self.classList = open(self.directory + "\\randomizer_info\\Class List.txt", 'r').read().split('\n')
        self.classDict = json.load(open(self.directory + "\\randomizer_info\\fe12classes.json"))
        self.disposDict = json.load(open(self.directory + "\\randomizer_info\\disposPointers.json"))
        self.proSkipDisposDict = json.load(open(self.directory + "\\randomizer_info\\skipDisposPointers.json"))
        self.enemyDict = json.load(open(self.directory + "\\randomizer_info\\disposList.json"))
        self.enemyGrowthDict = json.load(open(self.directory + "\\randomizer_info\\newEnemyClassGrowths.json"))

        self.slotList = open(self.directory + "\\randomizer_info\\internalChapterList.txt").read().split('\n')
        self.chapterDict = json.load(open(self.directory+"\\randomizer_info\\chaptersInOrder.json"))

        
        self.itemDict = json.load(open(self.directory+ "\\randomizer_info\\fe12items.json"))
        self.itemToGroup = json.load(open(self.directory + "\\randomizer_info\\itemToGroup.json"))
        self.groupToItem = json.load(open(self.directory + "\\randomizer_info\\groupToItem.json"))
        self.naturalWeaponsDict = json.load(open(self.directory + "\\randomizer_info\\fe12naturalWeapons.json"))
        
        self.itemToRank = json.load(open(self.directory + "\\randomizer_info\\itemToRank.json"))
        self.rankToItem = json.load(open(self.directory + "\\randomizer_info\\rankToItem.json"))

    def getSettings(self):
        settingsDict = {
            "Random Growths": self.randomGrowths,
            "Random Bases": self.randomBases,
            "Random Classes": self.randomClasses,
            "Random Portraits": self.randomCharacters,
            "Random Items": self.randomItems,
            "Random Enemies": self.randomEnemies,

            "Growths Range": self.growthsRange,

            "Enable Manaketes": self.enableManaketes,
            "Enable Ballisticians": self.enableBallistas,

            "Absolute Bases": self.absoluteBases,
            "Absolute Growths": self.absoluteGrowths,

            "Max Dancer Count": self.maxDancerCount,
            "Max Freelancer Count": self.maxFreelanceCount,
            
            "Mix Land and Flying Enemies": self.mixLandFlying,
            "Mix Human and Dragon Enemies": self.mixHumanDragon,
            
            "Uses Variance": self.itemUsesRange,
            "Might Variance": self.itemPowerRange,
            "Hit Variance": self.itemHitRange,
            "Crit Ratio": self.itemCritChance,
            "Crit Range": self.itemCritRange,
            
            "Truncate Prologue": self.noPrologue
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

        classBlacklist = ["Soldier", "Barbarian", "Pegasus Knight", "Emperor", "Mage Dragon",
                        "Earth Dragon", "Fire Dragon", "Ice Dragon", "Knight (F)",
                        "Wyvern", "Divine Dragon", "Shadow Dragon"]

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

                    classSet = [i for i in list(self.classDict) \
                        if i not in classBlacklist]

                    while True:
                        self.logDict[cName]["Class"] =  random.choice(classSet)
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
        

    def getNewEnemyClass(self,oldClassID,unitFlag="Normal"):
        
        flyingClasses = ["Pegasus Knight", "Falcon Knight", "Dracoknight", "Wyvern"]
        dragonClasses = ["Fire Dragon", "Wyvern", "Ice Dragon", "Mage Dragon"]
        #until AI changing is practical, healer classes are a no-go
        #Lord has no enemy growths
        #Chameleon has no AI behaviour
        #Female variants are accounted for later
        #Ballistician for now excluded from general pool
        forbiddenClasses = ["Lord", "Curate", "Cleric", "Pegasus Knight (F)", "Dracoknight (F)",
                            "Cavalier (F)", "Paladin (F)", "General (F)", "Archer (F)",
                            "Sniper (F)", "Myrmidon (F)", "Swordmaster (F)", "Mage (F)",
                            "Sage (F)", "Bishop (F)", "Manakete (F)","Knight (F)", "Emperor",
                            "Shadow Dragon", "Chameleon","Ballistician"]
        siegeUsers = [["Sage", "Bishop", "Sorcerer"], ["Ballistician"]]
        hasFemaleVariant = ["Dracoknight", "Cavalier", "Paladin", "General", "Archer", "Sniper",
                            "Myrmidon", "Swordmaster", "Mage", "Sage", "Bishop", "Manakete"]
        newClass = None
        oldClass = self.classList[oldClassID]
        if " (F)" in oldClass:
            oldClass = oldClass.replace(" (F)","")
        #print("Old Class: " + oldClass)
        if unitFlag == "Sieger":
            newClass = random.choice(random.choice(siegeUsers))
        else:
            oldTier = self.classDict[oldClass]["Tier"]
            if oldTier == "-" or unitFlag == "Keeper":
                return oldClass#for Emperor, Earth/Divine/Shadow Dragon
            if not self.mixLandFlying and oldClass not in flyingClasses:
                forbiddenClasses.extend(flyingClasses)
            if not self.enableManaketes:
                forbiddenClasses.append("Manakete")
            newClass = None
            tempList = [i for i in list(self.classDict) \
                        if i not in forbiddenClasses]
            if not self.mixLandFlying and oldClass in flyingClasses:
                tempList = flyingClasses
            elif unitFlag == "FliersOnly":
                tempList = flyingClasses
            elif unitFlag == "WaterOnly":
                tempList = flyingClasses
                tempList.extend(("Pirate", "Berserker", "Ice Dragon"))

            classSet = [i for i in tempList if self.classDict[i]["Tier"] == oldTier]
            if not self.mixHumanDragon:
                if oldClass in dragonClasses:
                    classSet = [i for i in classSet \
                                if i in dragonClasses]
                    #print(str(classSet))
                else:
                    classSet = [i for i in classSet \
                                if i not in dragonClasses]
            #print("New class set: " + str(classSet))
            newClass = random.choice(classSet)

        if newClass in hasFemaleVariant and random.randint(0,1) == 1:
            newClass = newClass + " (F)"
        return newClass
        
    def decryptCharacterGrowths(self,charIndex,growthList):
        newGrowths = []
        for g in range(8):
            cypherIndex = (growthList[g] - (0x57 * ((charIndex ^ 0x3E) - 3*g) ^ 0xF5)) & 0xFF
            actual = comp.twosComplement8(comp.cypherTable[cypherIndex])#convert unsigned to signed
            newGrowths.append(actual)
        return newGrowths
        
    def decryptClassGrowths(self,classIndex,growthList):
        newGrowths = []
        for g in range(8):
            cypherIndex = (growthList[g] - (0xB3 * ((classIndex ^ 0x9D) - 7*g) ^ 0xDB)) & 0xFF
            actual = comp.twosComplement8(comp.cypherTable[cypherIndex])
            newGrowths.append(actual)
        return newGrowths
        
    def encryptCharacterGrowths(self,charIndex,growthList):
        for g in range(8):
            actual = growthList[g]
            if actual < 0: actual = 256 + actual#converting signed to unsigned
            cypherIndex = comp.cypherTable.index(actual)
            encrypted = (cypherIndex + (0x57 * ((charIndex ^ 0x3E) - 3*g) ^ 0xF5)) & 0xFF
            growthList[g] = encrypted
        return growthList
        
    def encryptClassGrowths(self,classIndex,growthList):
        for g in range(8):
            actual = growthList[g]
            if actual < 0: actual = 256 + actual
            cypherIndex = comp.cypherTable.index(actual)
            encrypted = (cypherIndex + (0xB3 * ((classIndex ^ 0x9D) - 7*g) ^ 0xDB)) & 0xFF
            growthList[g] = encrypted
        return growthList


    def randomize(self, input_path, output_path, seed = None):
        try:
            #create output if doesn't exist
            if not os.path.exists(output_path+'\\data'):
                os.makedirs(output_path+'\\data')

            if not os.path.exists(output_path+'\\dispos'):
                os.makedirs(output_path+'\\dispos')
                
            if not os.path.exists(output_path+'\\script'):
                os.makedirs(output_path+'\\script')

            if os.path.exists(input_path+"\\data\\data"):
                input_path+= "\\data"

            #print(input_path+"\\dispos\\")
            if not os.path.exists(input_path+"\\dispos\\"):
                return "Error"
            
            if seed == None:
                seed = random.randint(-2147483647, 2147483647)




            #GDinput = bytearray(open(input_path+'\\data\\data\\FE12data.bin.rdcmp', 'rb').read())    
            #GDoutput = open(output_path+'\\data\\FE12data.bin.rdcmp', 'wb')
            
            #If we skip prologue, prologue units become stronger
            if self.noPrologue:
                self.ogDataDict.update(self.buffDataDict)
                self.disposDict.update(self.proSkipDisposDict)
                
             
            #Do things if we have skip prologue but no randomization of player units

            self.randomClassHelper(seed)

            #print(self.logDict)
            #print(self.rClassDict)
            if self.randomGrowths or self.randomBases or self.randomClasses or self.randomCharacters \
            or self.randomEnemies or self.randomItems or self.noPrologue:
                self.randomizeGameData(input_path+'\\data', seed, output_path +'\\data')

            #GDoutput.write(GDinput)
            #GDoutput.close() #merge output writing into gamedata function

            if self.randomClasses or self.randomEnemies or self.noPrologue:
                self.randomizeDispos(input_path+"\\dispos", seed, output_path+'\\dispos')
                
            if self.noPrologue:
                self.removePrologue(input_path+"\\script", output_path+"\\script")

            self.addMiscGraphics(output_path)

            self.randomizeScript(input_path+"\\m", seed, output_path + '\\m')

            self.status = " Randomization success! \n Please drag the data folder from the output back into  \n your unpacked directory and re-pack your ROM. \n\n (Make a copy for backup, just in case.)"

            self.writeLog(seed, output_path)


            return "helyea"

        except Exception as e:
            self.status = "Error"
            self.logger.exception("Exception on randomizer")
            #raise
            



    def removePrologue(self, input_path, output_path):
        print("Removing Prologue...")
        self.status = "Editing Prologue 1 events..."
        input = bytearray(open(input_path+'\\bmap201.cmb', 'rb').read())
        input[0x861],input[0x862],input[0x863] = 0x30,0x30,0x31#"001"
        
        result = open(output_path+'\\bmap201.cmb', "wb")
        result.write(input)
        result.close()
        return input

    
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
                    input[startingPointer + 42] = self.ogDataDict[randomizedChar]["Hair"]

                    self.replacementDict[cName] = randomizedChar
                


            #logData+= "Stats:\nHP/Str/Mag/Skl/Spd/Lck/Def/Res\n"
            
            if self.noPrologue and not self.randomBases:
                baseNames = "HP Str Mag Skl Spd Lck Def Res".split()
                for i in range(8):
                    newStat = self.ogDataDict[cName]["Bases"][baseNames[i]]
                    if newStat < 0: newStat += 256
                    input[startingPointer + 12 + i] = newStat
                wpnNames = "Sword Lance Axe Bow Magic Staff".split()
                for k in range(6):
                    input[startingPointer + 36 + k] = self.ogDataDict[cName]["Weapon Ranks"][wpnNames[k]]

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

                if self.randomClasses \
                    and (cName == "Tiki" or cName == "Bantu")  \
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
                
        
        #Make Prologue and Chapter 1 enemies weaker
        if not self.noPrologue:
            prologueList = list(range(97,110))
            prologueList.extend(list(range(140,177)))
            for enemyIndex in prologueList:
                startingPointer = enemyIndex*92 + 32
                growths = input[startingPointer+28:startingPointer+36]
                newGrowths = self.decryptCharacterGrowths(enemyIndex,growths)
                for i in range(8):
                    if i == 4: newGrowths[i] -= 10#Speed and HP especially
                    elif i == 0: newGrowths[i] -= 10
                    else: newGrowths[i] -= 5
                    if enemyIndex in [97,98,99]: newGrowths[i] -= 10#Jagen/Luke/Rody especially
                growths = self.encryptCharacterGrowths(enemyIndex,newGrowths)
                input[startingPointer+28:startingPointer+36] = growths
        
        #Random Enemies
        #For full random enemies (only choice rn), set Str and Mag to equal values
        #When we get around to having all enemies of the same character ID use the same
        #class, we could add more intelligent handling in that case.
        
        #We also negate most personal growths; generics have very significant personal growths
        #depending on their class, and we need to normalize class growths so that enemies
        #randomizing into or out of some classes don't end up with weird stats.
        
        
        if self.randomEnemies:
            for enemyIndex in range(111,337):
                if 139 < enemyIndex < 177: continue
                startingPointer = enemyIndex*92 + 32
                oldStrBase = int(input[startingPointer + 13])
                #oldStrBase = comp.twosComplement8(oldStrBase)
                
                oldMagBase = int(input[startingPointer + 14])
                #oldMagBase = comp.twosComplement8(oldMagBase)
                
                #If we have a negative base str/mag, it's probably for a reason!
                
                newBase = max(oldStrBase,oldMagBase)
                
                input[startingPointer + 13] = newBase
                input[startingPointer + 14] = newBase
                if enemyIndex not in [125,129]:
                    growths = [0,0,0,0,0,0,0,0]
                    if 299 < enemyIndex < 322:#Chapter 21+ enemies stronger
                        growths = [0,5,5,5,5,0,0,0]
                    elif enemyIndex in [178,182,183,191,198,204,205,213,214,216]:
                        growths = [0,-5,-5,-5,-5,0,0,0]#C2-C8 prepromotes weaker
                    growths = self.encryptCharacterGrowths(enemyIndex,growths)
                    input[startingPointer+28:startingPointer+36] = growths
                if 110 < enemyIndex < 140 or 246 < enemyIndex < 322:
                    for w in range(36,42):
                        input[startingPointer+w] = 0xC3
            for classIndex in range(56):
                startingPointer = classIndex*80 + 0x90F8
                adjustedGrowths = self.enemyGrowthDict[str(classIndex)]
                adjustedGrowths = self.encryptClassGrowths(classIndex,adjustedGrowths)
                input[startingPointer+24:startingPointer+32] = adjustedGrowths
        
        
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
                       
                

        if self.randomItems:
            self.state = "Randomizing weapons..."
            startingPointer = 41736
            for itemIndex in range(167):
                iName = self.itemDict[str(itemIndex+1)]
                if "Iron" in iName or iName == "Fire": continue#Make this an option
                itemPointer = startingPointer + 60*itemIndex
                itemType = int(input[itemPointer+16])
                if itemType == 5 or itemType > 7: continue
                self.itemLogDict[iName] = {}
                uses = int(input[itemPointer+20])
                if uses != 0:#Infinite-use weapons shouldn't have random uses
                    newMin = max(3,uses-self.itemUsesRange)
                    newMax = min(60,uses+self.itemUsesRange)
                    uses = random.randint(newMin,newMax)
                self.itemLogDict[iName]["Uses"] = uses
                input[itemPointer+20] = uses
                
                newPower = input[itemPointer+21] + random.randint(-self.itemPowerRange,self.itemPowerRange)
                newPower = max(0,newPower)
                #print(iName + " " + str(newPower))
                self.itemLogDict[iName]["Power"] = newPower
                input[itemPointer+21] = newPower
                newHit = input[itemPointer+22] + random.randrange(-self.itemHitRange,self.itemHitRange+1,5)
                newHit = max(0,min(newHit,255))
                self.itemLogDict[iName]["Hit"] = newHit
                input[itemPointer+22] = newHit
                oldCrit = int(input[itemPointer+23])
                if (random.randint(0,99) < self.itemCritChance) and oldCrit < 11 and iName not in ["Glower","Dark Breath"]:
                    newCrit = random.randrange(self.itemCritRange[0],self.itemCritRange[1]+1,5)
                    self.itemLogDict[iName]["Crit"] = newCrit
                    input[itemPointer+23] = newCrit
                else:
                    self.itemLogDict[iName]["Crit"] = oldCrit

        if self.removeWepLocks:
            #Remove weapon locks for Falchion, Wing Spear, Rapier, Hammerne and Aum
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
            startingPointer = 41736
            
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
            
        if self.enableBallistas:
            startingPointer = 41736
            for i in range(60,65):
                balPointer = startingPointer + 60*i + 43
                input[balPointer] = 0 #Remove no forging/enemy only flags




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

        #generate dict of characters and their respective randomized classes
        #write this to log as well


        mapList = "202 203 204 205 206 207 208 103 106 110 113 116 120 001 002 003 004 005 006 007 008 009 010 011 012 013 014 015 016 017 018 019 020 021 022 023 024".split()
        mapList = ["bmap"+ i for i in mapList]

        for map in mapList:
            print("Randomizing " + map + "...")

            self.status = "Randomizing " + map + "..."
            #iterate through each map
            #read map, decompress
            mapPath = input_path + "\\" + map 
            fe12_decompress(mapPath, mapPath+'.decmp')
            input = bytearray(open(mapPath+'.decmp', 'rb').read())
            
            if (self.randomClasses or self.noPrologue) and map in self.disposDict.keys():#Chapters 18 and 23 have no recruitables
                mapPlayerData = self.disposDict[map]
                input = self.updatePlayerClasses(input,mapPlayerData)
                
            if self.randomEnemies and map in self.enemyDict.keys():#We don't randomize prologue enemies, at least for now
                mapEnemyData = self.enemyDict[map]
                input = self.updateEnemyClasses(input,mapEnemyData)


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
        
    def updateEnemyClasses(self,input,mapData):
        baseOffset = mapData["Start"]
        limit = mapData["Count"]
        for unitIndex in range(limit):
            unitOffs = baseOffset + unitIndex*88
            charID = input[unitOffs] | (input[unitOffs+1] << 8)
            if charID < 78: continue#don't randomize player units here
            classID = input[unitOffs+2]
            unitFlag = "Normal"
            for flag in ["Sieger", "Keeper", "FliersOnly", "WaterOnly", "NeedsKey"]:
                if flag in mapData.keys() and unitIndex in mapData[flag]:
                    unitFlag = flag
                    break
            newClass = self.getNewEnemyClass(classID,unitFlag)#String
            newClassID = self.classDict[newClass]["Dispos Pointer"]
            if newClassID != classID:
                #Reassign weapons here
                #enemies with droppables turning into dragons need them moved, or inventory deleted?
                #siege enemies randomizing need some logic for Swarm-Meteor vs various ballistae
                #siege enemies who also have a melee tome - ??
                #weaponsChanged = 0
                classRanks = []
                if newClass == "Ballistician": classRanks = ["Ballista"]
                elif "Manakete" in newClass: classRanks = ["Dragonstone"]
                else:
                    for wepType,wepRank in self.classDict[newClass]["Weapon Ranks"].items():
                        if wepRank > 0 and wepType != "Staff": classRanks.append(wepType)
                for inv in [16,20,24,28]:
                    itemID = input[unitOffs+inv]
                    itemName = self.itemDict[str(itemID)]
                    
                    newItemID = 0
                    newItemType = None
                    itemRank,itemType = self.itemToRank[str(itemID)][0],self.itemToRank[str(itemID)][1]
                    noChange = ["None","Booster","Extra","DLC"]#Could differentiate further
                    if itemRank in noChange: continue#Special items (PRFs, starshards, etc) are left alone
                    if unitFlag == "Sieger" and newClass != "Ballistician":
                        if itemRank == "B": input[unitOffs+inv] = 55#Pachyderm becomes Meteor
                        else: input[unitOffs+inv] = 54#Others become Swarm
                        #weaponsChanged += 1
                        continue
                    
                    #Dragons shouldn't drop their breath weapons
                    if newClass in self.naturalWeaponsDict.keys():
                        newItemID = self.naturalWeaponsDict[newClass]
                        if input[unitOffs+inv+2] & 0x01 != 0:
                            #If dragon now and first weapon was droppable, shift three slots down
                            input[min(28,inv+12)] = input[unitOffs+inv]
                            input[min(30,inv+14)] = input[unitOffs+inv+2]
                            input[min(31,inv+15)] = input[unitOffs+inv+3]
                        input[unitOffs+inv] = newItemID
                        input[unitOffs+inv+2] = input[unitOffs+inv+2] & 0xFE
                        continue

                    #Determine weapon types from class's weapon ranks
                    #print(newClass + " " + str(classRanks) + " " + itemName)
                    newItemType = random.choice(classRanks)
                    newItemID = random.choice(self.rankToItem[itemRank][newItemType])
                    if newItemID == 70 and newClass != "Manakete (F)" and not self.abolishGender:
                        newItemID = random.choice([66,67,68,69])
                    #Longbow check
                    if newItemID == 43 and newClass not in ["Archer", "Sniper", "Archer (F)", "Sniper (F)"]:
                        newItemID = 40
                    if newItemID > 255: print(newItemID)
                    input[unitOffs+inv] = newItemID
                    if newItemID in [55,59]:#imhullu and Meteor shouldn't drop
                        input[unitOffs+inv+2] = input[unitOffs+inv+2] & 0xFE
                        
                        
                
            input[unitOffs+2] = newClassID
            
            
            
            if unitFlag == "NeedsKey":
                input[unitOffs+24] = 0x5D#inventory slot 3
            
        return input
        
    def updatePlayerClasses(self,input,mapData):
    #Updates classes, levels and inventory for all player units in a single map
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
            if "Level" in self.ogDataDict[cName]:
                newLev = self.ogDataDict[cName]["Level"]
                for pointer in mapData[cName]:
                    input[pointer+10] = newLev
                    input[pointer+11] = newLev
            if self.randomClasses and (cName not in ["Bantu", "Est", "Midia"] or self.logDict[cName]["Class"] != "Chameleon"):
                inventoryIterated = False 
                for pointer in mapData[cName]: #Thanks cecil now I have to iterate through pointers :/
                    #pointer = mapData[cName]


                    newClass = self.logDict[cName]["Class"]
                    #class pointer at input[pointer+3]
                    #Change class
                    input[pointer+3] = self.classDict[newClass]["Dispos Pointer"]
                    if cName == "Ryan" and not self.noPrologue:
                        input[pointer+25] = 96#Extra vuln
                        
                    if self.noPrologue and cName == "Marth":
                        input[pointer+29] = 133#compensate for no Prologue gold

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
                                    if maxWepRank < 45:
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
        return input

    
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
            if setting == "Growths Range" or setting == "Crit Range":
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
                    
        if self.randomItems:
            logData += "\n\nItem Data:"
            for item in self.itemLogDict:
                logData+= "\n\n" + item + "\n"
                stats = "Uses Might Hit Crit".split()
                for value in self.itemLogDict[item]:
                    logData += stats.pop(0) + " " + str(self.itemLogDict[item][value])
                    logData += " "

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




