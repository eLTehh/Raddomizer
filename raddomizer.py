import os 
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtTest import *
from click import File
from fe12dataReader import dataEditor
from superqt import QRangeSlider, QLabeledRangeSlider
import math
import random 
import json 

from functools import partial 
from threading import Thread 


class bigRaddomizer(QMainWindow): #I goofed by following a tutorial that started with qwidget...
    def __init__(self, parent = None):
        super(bigRaddomizer, self).__init__(parent)
        self.directory = os.getcwd()

        self.raddomizer = Raddomizer()
        self.setCentralWidget(self.raddomizer)

        self.resize(750, 800)
        self.setWindowTitle("FE12 Randomizer")
        self.setWindowIcon(QIcon(self.directory+"\\randomizer_assets\\marthicon.png"))
        self.windows = []


        menuBar = QMenuBar()
        fileMenu = menuBar.addMenu("File")
        importAction = fileMenu.addAction("Import Randomizer Settings")
        importAction.triggered.connect(self.importSettings)
        exportAction = fileMenu.addAction("Export Randomizer Settings")
        exportAction.triggered.connect(self.exportSettings)
        aboutAction = menuBar.addAction("About")
        aboutAction.triggered.connect(self.displayAbout)

        self.setMenuBar(menuBar)

    def importSettings(self):
        filePath = QFileDialog.getOpenFileName(self, "Load Exported Settings", filter = "JSON (*.json)")
        if filePath[0] != "":
            self.raddomizer.loadJson(filePath[0])


    def exportSettings(self):
        filePath = QFileDialog.getSaveFileName(self, "Save Exported Settings", filter = "JSON (*.json)")
        if filePath[0] != "":
            newFile = open(filePath[0], "w")
            json.dump(self.raddomizer.settingsDict, newFile)
            newFile.close()


    def displayAbout(self):
        newWin = aboutWindow(self.raddomizer.font, self.raddomizer.directory)
        self.windows.append(newWin)
        newWin.show()


    def closeEvent(self, ev):
        self.raddomizer.getSettings()

        jsonFile = open(self.directory + "//randomizer_info//recentSettings.json", "w")
        json.dump(self.raddomizer.settingsDict, jsonFile)
        jsonFile.close()


        ev.accept()


class Raddomizer(QWidget):
    def __init__(self, parent = None):

        super(Raddomizer, self).__init__(parent)
        self.directory = os.getcwd()
        self.randomizer = dataEditor(self.directory)
        self.rThread = None 
        self.settingsDict = {}


        self.windows = []

        self.initUI()
        self.initWindows()

        self.loadJson(self.directory + "//randomizer_info//recentSettings.json")



    def getSettings(self):

        self.settingsDict["Input"] = self.inOutDirectory[0].text()
        self.settingsDict["Output"] = self.inOutDirectory[1].text()

        for i in "Growths Bases Classes Portraits Items Enemies".split():
            self.settingsDict[i] = self.generalDict[i].getState()

        for j in "ManaketeFlag BallistaFlag AbsBases AbsGrowths WepLocks GenLocks MixHumanDragon MixLandFlying SkipPrologue".split():
            self.settingsDict[j] = self.advancedDict[j].getState()

        for k in "DancerCount FreelanceCount GrowthRange ItemMtDelta ItemHitDelta ItemUsesDelta ItemCritChance ItemCritRange".split():
            self.settingsDict[k] = self.advancedDict[k].getValue()

        self.settingsDict["Seed"] = self.advancedDict["Seed"].getSeed()

    def loadJson(self, jsonDir):
        if os.path.exists(jsonDir) and jsonDir.endswith(".json"):
            self.settingsDict  = json.load(open(jsonDir, "r"))
            self.loadSettings()

    def loadSettings(self):

        try:

            self.inOutDirectory[0].setText(self.settingsDict["Input"])
            self.inOutDirectory[1].setText(self.settingsDict["Output"])

            for i in "Growths Bases Classes Portraits Items Enemies".split():
                self.generalDict[i].setState(self.settingsDict[i])

            for j in "ManaketeFlag BallistaFlag AbsBases AbsGrowths WepLocks GenLocks MixHumanDragon MixLandFlying SkipPrologue".split():
                self.advancedDict[j].setState(self.settingsDict[j])

            for k in "DancerCount FreelanceCount GrowthRange ItemMtDelta ItemHitDelta ItemUsesDelta ItemCritChance ItemCritRange".split():
                self.advancedDict[k].setValue(self.settingsDict[k])   

            self.advancedDict["Seed"].setSeed(self.settingsDict["Seed"]) 
        except:
            self.settingsDict = {}



    def initWindows(self):
        #Directory stuff: 
        #X = center, Y = 0, columnspan = 5, rowspan = 2


        #self.miniGroup("Test", ("#392918","#392918","#100808", "#FFDCDC"), (20, 10), (30, 20))


        info = infoWindow(self.directory, self.font)
        self.grid.addWidget(info, 10, 20, 30, 30)#rows, cols

        self.inOutDirectory = self.directoryWindow(info, (0, 0), (50, 10))


        #Gen window:
        #X = 0, Y = 1, columnspan = 2, rowspan = 2
        genWin = self.miniGroup("General", ("#392918","#392918","#100808", "#FFDCDC"), info, (0,10), (20,30))#cols, rows

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        genWin.grid.addItem(spacer, 0, 0)


        #genWin.grid.setColumnStretch(1, 2)

        

        self.generalDict = {
            "Growths": self.addCheckBox(genWin, "Growths", info, 25, (1,1)),
            "Bases": self.addCheckBox(genWin, "Bases", info, 25, (1,2)),
            "Classes": self.addCheckBox(genWin, "Classes", info, 25, (1,3)), 
            "Portraits": self.addCheckBox(genWin, "Portraits", info, 25, (1,4)),
            "Items": self.addCheckBox(genWin, "Items", info, 25, (2,2)),
            "Enemies": self.addCheckBox(genWin, "Enemies", info, 25, (2,1))
            }




        #Character speaking
        #X = 1, Y = 1, columnspan = 3, rowspan = 2

        #Advanced:
        #X = center, Y = 2, columnspan = 5, rowspan = 3
        advancedWin = self.miniGroup("Advanced", ("#182039","#2d637b","#081018", "#ffffff"),info, (0,40), (50,40))
        


        advancedWin.grid.addItem(spacer, 0, 0, 10, 1)
        advancedWin.grid.addItem(spacer, 1, 0, 10, 1)
        advancedWin.grid.setSpacing(8)

        importButton = QPushButton(self)
        importButton.setFont(self.font)
        importButton.setText("Reroll")
        importButton.setStyleSheet("color: white;background-color: rgba(255, 255, 255, 50);")
        importButton.clicked.connect(self.rerollSeed)
        importButton.setMaximumWidth(80)

        advancedWin.grid.addWidget(importButton, 5, 4, 1, 1, Qt.AlignCenter)

        self.advancedDict = {
        "GrowthRange": self.addSlider(advancedWin, info, (1,2), (4,1), True),
        "AbsBases": self.addCheckBox(advancedWin, "Absolute Bases", info, 15, (1,3)),
        "AbsGrowths": self.addCheckBox(advancedWin, "Absolute Growths", info, 15, (2,3)),
        "ManaketeFlag": self.addCheckBox(advancedWin, "Enable Manaketes", info, 15, (1,4)),
        "BallistaFlag": self.addCheckBox(advancedWin, "Enable Ballisticians", info, 15, (2,4)),
        "DancerCount": self.addIntInput(advancedWin, "Max Dancers", info, -1, None, (1, 6)),
        "FreelanceCount": self.addIntInput(advancedWin, "Max Freelancers", info, -1, None, (2,6)),
        "ItemMtDelta": self.addIntInput(advancedWin, "Mt Variance", info, 0, 15, (1, 7)),
        "ItemHitDelta": self.addIntInput(advancedWin, "Hit Variance", info, 0, 50, (2, 7)),
        "ItemUsesDelta": self.addIntInput(advancedWin, "Uses Variance", info, 0, 30, (3,7)),
        "WepLocks": self.addCheckBox(advancedWin, "No Weapon Locks", info, -1, (1,5)),
        "GenLocks": self.addCheckBox(advancedWin, "No Gender Locks", info, -1, (2,5)),
        #Dragon
        
        "MixHumanDragon": self.addCheckBox(advancedWin, "Mix Human/Dragon", info, 15, (3,3)),
        "MixLandFlying": self.addCheckBox(advancedWin, "Mix Land/Flying", info, 15, (3,4)),
        "SkipPrologue": self.addCheckBox(advancedWin, "Skip Prologue", info, 12, (3,5)),
        "ItemCritRange": self.addSlider(advancedWin, info, (2,8), (2,1), False),
        "ItemCritChance": self.addIntInput(advancedWin, "Crit Chance", info, 0, 100, (1,8)),
        "Seed": self.addSeedInput(advancedWin, info, (4,3), (1, 2))
        }
        
        self.advancedDict["ItemHitDelta"].setStep(5)
        self.advancedDict["ItemUsesDelta"].setStep(2)
        self.advancedDict["ItemCritChance"].setStep(5)

        randomize = randomizeButton(self.font)
        randomize.clicked.connect(self.initRandomizer)
        #self.grid.addWidget(randomize, 54, 27, 5, 22)
        advancedWin.grid.addWidget(randomize, 6,4, 1, 1, Qt.AlignCenter)

    def initRandomizer(self):
        #print("Hi")
        inputPath = self.inOutDirectory[0].text()
        outputPath = self.inOutDirectory[1].text()

        if not os.path.exists(outputPath):
            outputPath = self.directory +"\\output\\data"
        else:
            outputPath += "\\output\\data"

        self.randomizer.randomGrowths = self.generalDict["Growths"].getState()
        self.randomizer.randomBases = self.generalDict["Bases"].getState()
        self.randomizer.randomClasses = self.generalDict["Classes"].getState()
        self.randomizer.randomCharacters = self.generalDict["Portraits"].getState()
        self.randomizer.randomItems = self.generalDict["Items"].getState()
        self.randomizer.randomEnemies = self.generalDict["Enemies"].getState()

        self.randomizer.enableManaketes = self.advancedDict["ManaketeFlag"].getState()
        self.randomizer.enableBallistas = self.advancedDict["BallistaFlag"].getState()

        self.randomizer.absoluteBases = self.advancedDict["AbsBases"].getState()
        self.randomizer.absoluteGrowths = self.advancedDict["AbsGrowths"].getState()

        self.randomizer.removeWepLocks = self.advancedDict["WepLocks"].getState()
        self.randomizer.abolishGender = self.advancedDict["GenLocks"].getState()
        self.randomizer.mixLandFlying = self.advancedDict["MixLandFlying"].getState()
        self.randomizer.mixHumanDragon = self.advancedDict["MixHumanDragon"].getState()
        self.randomizer.noPrologue = self.advancedDict["SkipPrologue"].getState()

        self.randomizer.maxDancerCount = self.advancedDict["DancerCount"].getValue()
        self.randomizer.maxFreelanceCount = self.advancedDict["FreelanceCount"].getValue()

        self.randomizer.growthsRange = self.advancedDict["GrowthRange"].getValues()
        
        self.randomizer.itemPowerRange = self.advancedDict["ItemMtDelta"].getValue()
        self.randomizer.itemHitRange = self.advancedDict["ItemHitDelta"].getValue()
        self.randomizer.itemUsesRange = self.advancedDict["ItemUsesDelta"].getValue()
        self.randomizer.itemCritChance = self.advancedDict["ItemCritChance"].getValue()
        self.randomizer.itemCritRange = self.advancedDict["ItemCritRange"].getValues()



        seed = self.advancedDict["Seed"].getSeed()

        if not os.path.exists(inputPath+"\\data\\dispos\\") and not os.path.exists(inputPath+"\\dispos\\"):
            error = errorWindow(self.font, self.directory, '''
            <div style = "text-align:center">
            &nbsp;&nbsp;Make sure your input directory&nbsp;&nbsp;<br>
            &nbsp;&nbsp;contains an <b><i>unpacked</i></b> FE12 ROM folder.&nbsp;&nbsp;
            <br><br>
            &nbsp;&nbsp;Please click "Help" for more information.&nbsp;&nbsp;
            </div>
            ''')
            self.windows.append(error)
            error.show()

        else:

            loadScreen = randomLoadScreen(self.directory, self.font, self.randomizer, inputPath, outputPath, seed)
            self.windows.append(loadScreen)
            loadScreen.show()
            loadScreen.randomize()

    def initUI(self):


        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.setContentsMargins(16,8,16,8) #left, top, right, bottom
        self.grid.setSpacing(16)

        #font
        chiaroID = QFontDatabase.addApplicationFont(self.directory + "\\randomizer_assets\\FOT-ChiaroStd-B.otf")
        chiaro = QFontDatabase.applicationFontFamilies(chiaroID)



        palette = QPalette()
        palette.setColor(QPalette.Text, Qt.white)

        self.font = QFont()
        self.font.setFamily(chiaro[0])
        self.font.setStyleStrategy(QFont.PreferAntialias)


        #self.font.setPointSize(12)


    def rerollSeed(self):
        self.advancedDict["Seed"].reroll()

    def addText(self, widget, text, position = (0,0), spanpos = (1,1)):

        col = position[0]
        row = position[1]

        colspan = spanpos[0]
        rowspan = spanpos[1]
    


        label = dynamicLabel(self)
        label.setText(text)
        label.setFont(self.font)
        widget.grid.addWidget(label, row, col, rowspan, colspan)

        return label

    def addInputField(self, widget, position = (0,0), spanpos = (1,1)):
        col = position[0]
        row = position[1]

        colspan = spanpos[0]
        rowspan = spanpos[1]

        label = QLineEdit(self)
        label.setFont(self.font)

        widget.grid.addWidget(label, row, col, rowspan, colspan)

        return label 

    def addIntInput(self, widget, text, info, min = None, max = None, position = (0,0), spanpos = (1, 1)):
        col = position[0]
        row = position[1]

        colspan = spanpos[0]
        rowspan = spanpos[1]       

        label = intInputLabel(text, self.font, info)

        if min is not None:
            label.setMinimum(min)
            
        if max is not None:
            label.setMaximum(max)

        widget.grid.addWidget(label, row, col, rowspan, colspan)

        return label 
 
    def addSeedInput(self, widget, info, position = (0,0), spanpos = (1, 1)):
        col = position[0]
        row = position[1]

        colspan = spanpos[0]
        rowspan = spanpos[1]       

        label = seedLabel(self.font, info)

        widget.grid.addWidget(label, row, col, rowspan, colspan)

        return label 

    def addCheckBox(self, widget, text, info, minSize = 25, position = (0,0), spanpos = (1,1)):
        col = position[0]
        row = position[1]

        colspan = spanpos[0]
        rowspan = spanpos[1]


        checkBox = randomizerCheckbox(text, self.font, info, minSize)

        widget.grid.addWidget(checkBox, row, col, rowspan, colspan)

        return checkBox 

    def addSlider(self, widget, info, position = (0,0), spanpos = (1,1), growth = True):

        col = position[0]
        row = position[1]

        colspan = spanpos[0]
        rowspan = spanpos[1]
        newSlider = None
        
        if growth == True:
            newSlider = customStepSlider(self.font, info)
        else:
            newSlider = critStepSlider(self.font, info)
        widget.grid.addWidget(newSlider, row, col, rowspan, colspan )
        return newSlider
        


    def miniGroup(self, title, colors, info, position = (0,0), spanpos = (1,1)):
        col = position[0]
        row = position[1]

        colspan = spanpos[0]
        rowspan = spanpos[1]

        rect = miniGroup(colors[0], colors[1], colors[2], colors[3], self.font, info)
        label = windowLabel(title, "#182039","#2d637b","#081018", self.font)


        self.grid.addWidget(rect, row, col, rowspan, colspan)
        self.grid.addWidget(label, row, col+1, 4, len(title)+1)        

        return rect 
        

    def directoryWindow(self, info, position = (0,0), spanpos = (1,1)):
        col = position[0]
        row = position[1]

        colspan = spanpos[0]
        rowspan = spanpos[1]

        rect = directoryWindow(info)

        #folderPath = QFileDialog.getExistingDirectory(self, 'Select ROM directory')




        self.addText(rect,"Unpacked ROM Directory:", (0, 0), (3, 1))
        self.addText(rect,"Output Directory (optional):", (0, 1), (3, 1))

        unpackedROMDir = self.addInputField(rect, (3,0), (5,1))
        outputDir = self.addInputField(rect, (3,1), (5,1))
        #rect.addWidget(folderPath, 0, 1)


        helpButton = QPushButton(self)
        helpButton.setFont(self.font)
        helpButton.setText("Help")
        helpButton.setIcon(QIcon(self.directory +"\\randomizer_assets\\questioncircle.svg"))
        helpButton.setStyleSheet("color: white;background-color: rgba(255, 255, 255, 50);")
        helpButton.setToolTip("Click for detailed information")
        helpButton.clicked.connect(self.showRomInfo)
        rect.grid.addWidget(helpButton, 0, 10)


        romButton = QPushButton(self)
        romButton.setText("...")
        romButton.clicked.connect(lambda: self.promptDirectory('Select ROM directory', unpackedROMDir))
        rect.grid.addWidget(romButton, 0, 8)

        outputButton = QPushButton(self)
        outputButton.setText("...")
        outputButton.clicked.connect(lambda: self.promptDirectory('Select output directory', outputDir))
        rect.grid.addWidget(outputButton, 1, 8)

        self.grid.addWidget(rect, row, col, rowspan, colspan)

        return [unpackedROMDir, outputDir]

    def promptDirectory(self, text, label):
        folderPath = QFileDialog.getExistingDirectory(self, text)
        label.setText(folderPath)


    def showRomInfo(self):
        newWindow = romInfoWindow(self.font, self.directory)
        self.windows.append(newWindow)
        newWindow.show()


    def paintEvent(self, ev):
        painter = QPainter(self)


        gradient = QLinearGradient(QRectF(self.rect()).topLeft(),QRectF(self.rect()).topRight())
        gradient.setColorAt(0.0, QColor("#204152"))
        gradient.setColorAt(1.0, QColor("#204152"))
        gradient.setColorAt(0.5, QColor("#418b8b"))
        gradient.setColorAt(0.25, QColor("#296273"))
        gradient.setColorAt(0.75, QColor("#296273"))

        painter.setBrush(gradient)
        painter.drawRect(self.rect())


#Windows
class romInfoWindow(QWidget):
    def __init__(self, font, directory, parent = None):
        super(romInfoWindow, self).__init__(parent) 
        self.font = font 
        self.directory = directory 
        self.setWindowIcon(QIcon(self.directory+"\\randomizer_assets\\infocircle.svg"))

        self.resize(500, 800)
        self.setWindowTitle("Help")
        
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        infoImage1 = resizeImageLabel(self.directory + "//randomizer_assets//rodyfiles.png")
        infoImage2 = resizeImageLabel(self.directory + "//randomizer_assets//lukefiles.png")


        text1 = self.customTextLabel("  Please make sure your directory looks like the following:  ")

        text2 = self.customTextLabel("  You can use a tool like DSLazy to unpack your ROM.  ")

        text3 = self.customTextLabel("  For more detailed instructions, you can check the \n  readme bundled with the program.  ")


        self.grid.addWidget(text1, 0, 0, 3, 5)

        self.grid.addWidget(text2, 42, 0, 3, 5)
        self.grid.addWidget(infoImage1, 3, 0, 40,5)
        self.grid.addWidget(infoImage2, 45, 0, 20, 5)
        self.grid.addWidget(text3, 69, 0, 6, 5)


        button = QPushButton(self)
        button.setText("OK")
        button.setFont(self.font)
        button.setStyleSheet("color: white;background-color: #182039;")
        button.clicked.connect(self.close)

        self.grid.addWidget(button, 80, 0, 1, 5)


    def initBG(self, widget):
        
        dColor = QColor("#182039")
        dColor.setAlphaF(0.70)


        widget.setAutoFillBackground(True)

        palette = widget.palette()
        palette.setColor(widget.backgroundRole(), dColor)
        widget.setPalette(palette)

    def customTextLabel(self, text):
        textLabel = QLabel()
        textLabel.setText(text)
        textLabel.setFont(self.font)
        textLabel.setFixedWidth(520)
        textLabel.setStyleSheet("color:white; font-size: 19px;")

        self.initBG(textLabel)

        return textLabel

    def paintEvent(self, ev):
        painter = QPainter(self)


        gradient = QLinearGradient(QRectF(self.rect()).topLeft(),QRectF(self.rect()).topRight())
        gradient.setColorAt(0.0, QColor("#204152"))
        gradient.setColorAt(1.0, QColor("#204152"))
        gradient.setColorAt(0.5, QColor("#418b8b"))
        gradient.setColorAt(0.25, QColor("#296273"))
        gradient.setColorAt(0.75, QColor("#296273"))

        painter.setBrush(gradient)
        painter.drawRect(self.rect())    

class errorWindow(QWidget):
    def __init__(self, font, directory, errorText, parent = None):
        super(errorWindow, self).__init__(parent) 
        self.font = font 
        self.directory = directory 
        self.setWindowIcon(QIcon(self.directory+"\\randomizer_assets\\infocircle.svg"))

        self.resize(450, 550)
        self.setWindowTitle("ERROR")
        
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        errorImage = resizeImageLabel(self.directory + "//randomizer_assets//error.png")


        text1 = self.customTextLabel("  Whoops, we've run into an error!  ")

        text2 = self.customTextLabel(errorText)


        self.grid.addWidget(text1, 0, 0, 3, 5, Qt.AlignCenter)

        self.grid.addWidget(text2, 43, 0, 5, 5, Qt.AlignCenter)

        self.grid.addWidget(errorImage, 3, 0, 40,5)


        button = QPushButton(self)
        button.setText("OK")
        button.setFont(self.font)
        button.setStyleSheet("color: white;background-color: #182039;")
        button.clicked.connect(self.close)

        self.grid.addWidget(button, 65, 0, 1, 5)


    def initBG(self, widget):
        
        dColor = QColor("#182039")
        dColor.setAlphaF(0.70)


        widget.setAutoFillBackground(True)

        palette = widget.palette()
        palette.setColor(widget.backgroundRole(), dColor)
        widget.setPalette(palette)

    def customTextLabel(self, text):
        textLabel = QLabel()
        textLabel.setText(text)
        textLabel.setFont(self.font)
        textLabel.setStyleSheet("color: white;")

        self.initBG(textLabel)

        return textLabel

    def paintEvent(self, ev):
        painter = QPainter(self)


        gradient = QLinearGradient(QRectF(self.rect()).topLeft(),QRectF(self.rect()).topRight())
        gradient.setColorAt(0.0, QColor("#204152"))
        gradient.setColorAt(1.0, QColor("#204152"))
        gradient.setColorAt(0.5, QColor("#418b8b"))
        gradient.setColorAt(0.25, QColor("#296273"))
        gradient.setColorAt(0.75, QColor("#296273"))

        painter.setBrush(gradient)
        painter.drawRect(self.rect())                

class infoWindow(QWidget):
    def __init__(self, directory, font, parent = None):
        super(infoWindow, self).__init__(parent)    

        self.font = font 
        #portraitcoords = [(windowSize[2]//124)*124, (windowSize[3]//102)*102]

        self.defaultText = "Welcome to the Raddomizer!\nHover over the settings for more information."


        self.directory = directory

        self.raddLabel = resizeImageLabel(self.directory + "\\randomizer_assets\\raddsprite.png")
        self.backgroundLabel = resizeImageLabel(self.directory + "\\randomizer_assets\\bg1.png")


        self.grid = QGridLayout()
        self.setLayout(self.grid)

        spacer = QSpacerItem(40, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.dialogueLabel = infoText(self.defaultText, font)
        #self.testlabel.setText("Play Ghost Trick")


        self.grid.addWidget(self.backgroundLabel, 0, 0, 12, 10)
        self.grid.addWidget(self.raddLabel, 1, 0, 9, 10)
        self.grid.addWidget(self.dialogueLabel, 8, 0, 4, 10)
        #self.grid.addItem(spacer, 10, 10)

    def changeText(self, text):
        self.dialogueLabel.insertText(text)

    def changeDefault(self): 
        self.dialogueLabel.insertText(self.defaultText)
      
class smallInfoWindow(QWidget):
    def __init__(self, directory, font, parent = None):
        super(smallInfoWindow, self).__init__(parent)    

        self.font = font 

        self.defaultText = "Don't close the program while it randomizes.\nRecompression may take some time."


        self.directory = directory    

        self.raddLabel = resizeImageLabel(self.directory + "\\randomizer_assets\\raddsprite.png")
        self.backgroundLabel = resizeImageLabel(self.directory + "\\randomizer_assets\\bg1.png")


        self.grid = QGridLayout()
        self.setLayout(self.grid)

        spacer = QSpacerItem(40, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.dialogueLabel = infoText(self.defaultText, font)

        self.grid.addWidget(self.backgroundLabel, 0, 0, 12, 10)
        self.grid.addWidget(self.raddLabel, 1, 0, 9, 10)
        self.grid.addWidget(self.dialogueLabel, 8, 0, 4, 10)

    def changeText(self, text):
        self.dialogueLabel.insertText(text)

    def changeDefault(self): 
        self.dialogueLabel.insertText(self.defaultText)

class randomLoadScreen(QWidget):
    def __init__(self, directory, font, randomizer, inputPath, outputPath, seed, parent = None):
        super(randomLoadScreen, self).__init__(parent)  
        self.resize(600, 400)

        self.font = font 
        self.directory = directory

        self.setWindowTitle("Randomization in progress...")
        self.setWindowIcon(QIcon(self.directory+"\\randomizer_assets\\marthicon.png"))


        self.grid = QGridLayout()
        self.setLayout(self.grid)



        self.loadLabel = self.customTextLabel("Randomization started.")
        self.infoLabel = smallInfoWindow(self.directory, self.font)

        self.grid.addWidget(self.infoLabel, 0, 0, 3, 1)
        self.grid.addWidget(self.loadLabel, 4, 0, 1, 1)

        self.randomizer = randomizer 
        self.inputPath = inputPath 
        self.outputPath = outputPath 
        self.seed = seed


    def randomize(self):
        rThread = Thread(target = self.randomizer.randomize, args = (self.inputPath, self.outputPath, self.seed))
        
        rThread.start() 

        while rThread.is_alive:
            QTest.qWait(10)
            self.loadLabel.setText(self.randomizer.status)

            if "Randomization success!" in self.randomizer.status:
                self.infoLabel.changeText("That's Radd")
                self.infoLabel.setFixedSize(30, 30)
                tutorial = resizeImageLabel(self.directory + "\\randomizer_assets\\outputtuto.png")
                self.grid.addWidget(tutorial, 0, 0, 3, 1)
                self.resize(600, 600)
                self.setWindowTitle("Success!")
                break 

            if self.randomizer.status == "Error":
                self.infoLabel.changeText("Oof")
                self.loadLabel.setText("The randomizer has run into an error. \nPlease report the error by sending error.log, \nas well as your randomizer settings.")
                self.setWindowTitle("Error")

                break
        button = QPushButton(self)
        button.setText("OK")
        button.setFont(self.font)
        button.setStyleSheet("color: white;background-color: #182039;")
        button.clicked.connect(self.close)

        self.grid.addWidget(button, 20, 0, 1, 1)


    def initBG(self, widget):
        
        dColor = QColor("#182039")
        dColor.setAlphaF(0.70)


        widget.setAutoFillBackground(True)

        palette = widget.palette()
        palette.setColor(widget.backgroundRole(), dColor)
        widget.setPalette(palette)

    def customTextLabel(self, text):
        textLabel = QLabel()
        textLabel.setText(text)
        textLabel.setFont(self.font)
        textLabel.setStyleSheet("color: white;")

        self.initBG(textLabel)

        return textLabel


    def paintEvent(self, ev):
        painter = QPainter(self)


        gradient = QLinearGradient(QRectF(self.rect()).topLeft(),QRectF(self.rect()).topRight())
        gradient.setColorAt(0.0, QColor("#204152"))
        gradient.setColorAt(1.0, QColor("#204152"))
        gradient.setColorAt(0.5, QColor("#418b8b"))
        gradient.setColorAt(0.25, QColor("#296273"))
        gradient.setColorAt(0.75, QColor("#296273"))

        painter.setBrush(gradient)
        painter.drawRect(self.rect())  

class directoryWindow(QWidget):
    def __init__(self, info, parent = None):
        super(directoryWindow, self).__init__(parent)   
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.setAttribute(Qt.WA_Hover)
        self.infoConnection = info 



        dColor = QColor("#182039")
        dColor.setAlphaF(0.70)


        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), dColor)
        self.setPalette(palette)

    def event(self, event):
        if event.type() == QEvent.HoverEnter:
            self.infoConnection.changeText("The input directory should contain \nan unpacked FE12 ROM.")
            pass
        elif event.type() == QEvent.HoverLeave:
            #print("leave")
            #Halt signal
            self.infoConnection.changeDefault()
            
            pass
        return super().event(event)     

#Widgets/Groups
class randomizeButton(QPushButton):
    def __init__(self, font, parent = None):
        super(randomizeButton, self).__init__(parent)


        self.setStyleSheet("margin: 10px")

        self.setFixedSize(210, 60)

        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.font = font 
        self.font.setPointSize(15)

    
    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.setRenderHints( QPainter.HighQualityAntialiasing )

        gradient = QLinearGradient(QRectF(self.rect()).topLeft(),QRectF(self.rect()).bottomLeft())
        gradient.setColorAt(0.0, QColor("#ffec86"))
        gradient.setColorAt(0.5, QColor("#ddaf58"))
        gradient.setColorAt(1.0, QColor("#ffec86"))

        painter.setBrush(gradient)
        painter.drawRoundedRect(self.rect(), 5.0, 5.0)

        rectPath = QPainterPath()
        rectPath.addRoundedRect(QRectF(self.rect()), 5.5, 5.5)
        painter.setPen(QPen(Qt.black, 5, Qt.SolidLine,
                                 Qt.RoundCap, Qt.RoundJoin))
        painter.drawPath(rectPath)

        text = QPainterPath()
        text.addText(36, 40, self.font, "Randomize!")
        
        painter.setPen(QPen(Qt.black, 5, Qt.SolidLine,
                                 Qt.RoundCap, Qt.RoundJoin))
        painter.drawPath(text)

        #painter.setBrush(Qt.white)

        painter.fillPath(text, Qt.white)

class windowLabel(QWidget):
    def __init__(self, title, baseColor, embossColor, shadowColor, font, parent = None):
        super(windowLabel, self).__init__(parent)
        
        self.baseColor = baseColor 
        self.embossColor = embossColor
        self.shadowColor = shadowColor
        self.font = font

        self.grid = QGridLayout()
        self.setLayout(self.grid)  

        self.grid.setContentsMargins(10, 5, 10, 5)


        label = dynamicLabel(self)
        label.setText(title)
        label.setFont(self.font)
        label.setAlignment(Qt.AlignCenter)
        self.grid.addWidget(label)

    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.setRenderHints( QPainter.HighQualityAntialiasing )

        gradient = QLinearGradient(QRectF(self.rect()).topLeft(),QRectF(self.rect()).bottomLeft())
        gradient.setColorAt(0.0, QColor(self.embossColor))
        gradient.setColorAt(0.1, QColor(self.embossColor))
        gradient.setColorAt(0.2, QColor(self.baseColor))

        yMidPoint = QRectF(self.rect()).center().y()

        sideShadows = QLinearGradient(QRectF(self.rect()).left(), yMidPoint, QRectF(self.rect()).right(), yMidPoint)
        sideShadows.setColorAt(0.1, Qt.transparent)
        sideShadows.setColorAt(0.90, Qt.transparent)
        sideShadows.setColorAt(0.0, QColor(self.shadowColor))
        sideShadows.setColorAt(1.0, QColor(self.shadowColor))


        
        painter.setBrush(gradient)
        painter.drawRoundedRect(self.rect(), 5.0, 5.0)
        painter.setBrush(sideShadows)
        painter.drawRoundedRect(self.rect(), 5.0, 5.0)

        rectPath = QPainterPath()
        rectPath.addRoundedRect(QRectF(self.rect()), 5.5, 5.5)
        painter.setPen(QPen(Qt.white, 5, Qt.SolidLine,
                                 Qt.RoundCap, Qt.RoundJoin))
        painter.drawPath(rectPath)

class intInputLabel(QWidget):
    def __init__(self, text, font, info, parent = None):
        super(intInputLabel, self).__init__(parent)
        self.setAttribute(Qt.WA_Hover)
        self.infoConnection = info

        self.text = text 

        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.grid.setContentsMargins(1,4, 1,4)

        self.label = dynamicLabel()
        self.label.setText(text)
        self.label.setFont(font)
        self.label.setMinSize(20)
        self.label.setStyleSheet("color: white;")  

        self.inputField = QSpinBox()
        self.inputField.setValue(1)
        self.inputField.setFont(font)
        self.inputField.setStyleSheet("color:black")
        self.inputField.setMaximumSize(40, 40)

        self.grid.addWidget(self.label, 0, 0, 1, 2, Qt.AlignCenter)
        self.grid.addWidget(self.inputField, 0, 2, 1, 1, Qt.AlignCenter)

        self.dialogueDict = {
            "Max Dancers": "Max amount of Dancers to \nbe randomized. -1 means unlimited.",
            "Max Freelancers": "Max amount of Freelancers \nto be randomized. -1 means unlimited.",
            "Mt Variance": "Max amount to add or subtract\n from each weapon's Mt.",
            "Hit Variance": "Max amount to add or subtract\n from each weapon's Hit.",
            "Uses Variance": "Max amount to add or subtract\n from each weapons's durability.",
            "Crit Chance": "Chance for each weapon\n to gain crit if it had none."
        }
         
    def getValue(self):
        return self.inputField.value()

    def setValue(self, value):
        self.inputField.setValue(value)


    def setMinimum(self, min):
        self.inputField.setMinimum(min)
        
    def setMaximum(self,max):
        self.inputField.setMaximum(max)
        
    def setStep(self,step):
        self.inputField.setSingleStep(step)
    
    def event(self, event):
        if event.type() == QEvent.HoverEnter:
            #Send signal
            #print("enter")
            self.infoConnection.changeText(self.dialogueDict[self.text])
            pass
        elif event.type() == QEvent.HoverLeave:
            #print("leave")
            #Halt signal
            
            pass
        return super().event(event)

class seedLabel(QWidget):
    def __init__(self, font, info, parent = None):
        super(seedLabel, self).__init__(parent)

        self.setAttribute(Qt.WA_Hover)
        self.infoConnection = info


        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.grid.setContentsMargins(1,4, 1,4)

        self.label = dynamicLabel()
        self.label.setText("Seed")
        self.label.setFont(font)
        self.label.setMinSize(25)
        self.label.setStyleSheet("color: white;")  

        self.inputField = QLineEdit()
        self.inputField.setFont(font)
        self.inputField.setStyleSheet("font-size: 20px; color: black;")  
        self.inputField.setAlignment(Qt.AlignCenter)
        self.inputField.setMinimumSize(100, 40)


        seed = random.randint(-2147483647, 2147483647) #Initial Seed
        self.inputField.setText(str(seed))

        self.grid.addWidget(self.label, 0, 0, 1, 1, Qt.AlignCenter)
        self.grid.addWidget(self.inputField, 1, 0, 1, 1, Qt.AlignCenter)

    def getSeed(self):
        return self.inputField.text()

    def setSeed(self,seed):
        self.inputField.setText(seed)

    def reroll(self):
        seed = random.randint(-2147483647, 2147483647) #Initial Seed
        self.inputField.setText(str(seed))
    
    def event(self, event):
        if event.type() == QEvent.HoverEnter:
            #Send signal
            #print("enter")
            self.infoConnection.changeText("Influences RNG. Using the same seed \ngives you the same RNG result.")
            pass
        elif event.type() == QEvent.HoverLeave:
            #print("leave")
            #Halt signal
            
            pass
        return super().event(event)

class miniGroup(QWidget):
    def __init__(self, baseColor, embossColor, shadowColor, strokeColor, font, info, parent = None):
        super(miniGroup, self).__init__(parent)

        self.setAttribute(Qt.WA_Hover)
        self.infoConnection = info 

        
        self.baseColor = baseColor 
        self.embossColor = embossColor
        self.shadowColor = shadowColor
        self.strokeColor = strokeColor
        self.font = font
        self.setStyleSheet("color: white;")


        self.grid = QGridLayout()
        self.setLayout(self.grid)
        #self.grid.setContentsMargins(10, -1, 10, -1)
        #self.grid.setSpacing(0)

        
    def event(self, event):
        if event.type() == QEvent.HoverEnter:
            pass
        elif event.type() == QEvent.HoverLeave:
            #print("leave")
            #Halt signal
            self.infoConnection.changeDefault()
            
            pass
        return super().event(event)        


    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.setRenderHints( QPainter.HighQualityAntialiasing )

        gradient = QLinearGradient(QRectF(self.rect()).topLeft(),QRectF(self.rect()).bottomLeft())
        gradient.setColorAt(0.0, QColor(self.embossColor))
        gradient.setColorAt(0.07, QColor(self.embossColor))
        gradient.setColorAt(0.1, QColor(self.baseColor))

        yMidPoint = QRectF(self.rect()).center().y()

        sideShadows = QLinearGradient(QRectF(self.rect()).left(), yMidPoint, QRectF(self.rect()).right(), yMidPoint)
        sideShadows.setColorAt(0.1, Qt.transparent)
        sideShadows.setColorAt(0.90, Qt.transparent)
        sideShadows.setColorAt(0.0, QColor(self.shadowColor))
        sideShadows.setColorAt(1.0, QColor(self.shadowColor))



        coords = self.rect().getCoords()
        
        painter.setBrush(gradient)
        painter.drawRoundedRect(coords[0], coords[1]+20, coords[2], coords[3]-20, 5.0, 5.0)
        
        painter.setBrush(sideShadows)
        painter.drawRoundedRect(coords[0], coords[1]+20, coords[2], coords[3]-20, 5.0, 5.0)

        rectPath = QPainterPath()
        rectPath.addRoundedRect(coords[0], coords[1]+20, coords[2], coords[3]-20, 5.5, 5.5)
        painter.setBrush(gradient)

        painter.setPen(QPen(QColor(self.strokeColor), 3, Qt.SolidLine,
                                 Qt.RoundCap, Qt.RoundJoin))
        painter.drawPath(rectPath)

class randomizerCheckbox(QWidget):
    def __init__(self, text, font, info, minSize = 25, parent = None):
        super(randomizerCheckbox, self).__init__(parent)

        self.name = text 

        self.setAttribute(Qt.WA_Hover)

        self.infoConnection = info 

        self.checkbox = QCheckBox()
        self.checkbox.setStyleSheet("QCheckBox::indicator { width: 25px; height: 25px;}")
        self.checkbox.stateChanged.connect(self.onChecked)


        self.label = dynamicLabel()
        self.label.setText(text)
        self.label.setFont(font)
        self.label.setMinSize(minSize)
        self.label.setStyleSheet("color: #b5b5b5;")  


        self.grid = QGridLayout()
        self.setLayout(self.grid)
        #self.grid.setSpacing(0)
        self.grid.setContentsMargins(1,4, 1,4)

        self.grid.addWidget(self.checkbox, 0, 0, 1, 1)
        self.grid.addWidget(self.label, 0, 1, 1, 10)

        self.dialogueDict = {
            "Growths":"Randomizes growth rates of \nall playable characters.",
            "Bases": "Randomizes bases of all \nplayable characters.",
            "Classes":"Randomizes classes of all \nplayable characters (except Kris).",
            "Portraits":"Randomizes identities (e.g. Marth -> Radd) \nof all playable characters (except Kris).",
            "Items": "Randomizes weapon stats \n(Mt, Hit and Crit).",
            "Enemies": "Randomizes enemy classes\n and inventories.",
            "Absolute Bases": "Ignores whether bases add \nup to the original base stat total.",
            "Absolute Growths": "Ignores whether growths add \nup to the original base stat total.",
            "Enable Manaketes": "Adds non-divine Manaketes \ninto the player class pool.",
            "Enable Ballisticians": "Adds Ballisticians into \nthe player class pool.",
            "No Weapon Locks": "Makes Falchion, Rapier, Wing Spear, \nHammerne and Aum available to all.",
            "No Gender Locks":"Removes gender lock for weapons.\nUseful if randomizing classes/portraits.",
            "Mix Land/Flying":"Allows grounded enemies to become\n fliers and vice versa (where possible).",
            "Mix Human/Dragon":"Allows enemy Dragons to become\nhuman and vice versa.",
            "Skip Prologue":"Removes Prologues 2-8.\nPrologue units start at higher levels."
        }
        
    def setState(self, state):
        self.checkbox.setChecked(state)

    def getState(self):

        return self.checkbox.isChecked()

    def onChecked(self, state):
        if state != Qt.Checked:
            #print("Working")
            self.label.setStyleSheet("color: #b5b5b5;")  

        else:
            self.label.setStyleSheet("color: white;")      
    
    def event(self, event):
        if event.type() == QEvent.HoverEnter:
            #Send signal
            #print("enter")
            self.infoConnection.changeText(self.dialogueDict[self.name])
            pass
        elif event.type() == QEvent.HoverLeave:
            #print("leave")
            #Halt signal
            
            pass
        return super().event(event)

class dynamicLabel(QLabel):
    #modified from: https://stackoverflow.com/questions/29852498/syncing-label-fontsize-with-layout-in-pyqt
    def __init__(self, *args, **kargs):
        super(dynamicLabel, self).__init__(*args, **kargs)

        self.setSizePolicy(QSizePolicy(QSizePolicy.Ignored,
                                             QSizePolicy.Ignored))  

        self.setMinSize(14)

        self.setStyleSheet("color: white;")


    def setMinSize(self, minfs):        

        f = self.font()
        f.setPixelSize(minfs)
        br = QFontMetrics(f).boundingRect(self.text())

        self.setMinimumSize(br.width(), br.height())

    def resizeEvent(self, event):
        super(dynamicLabel, self).resizeEvent(event)

        if not self.text():
            return

        #--- fetch current parameters ----

        f = self.font()
        cr = self.contentsRect()

        #--- find the font size that fits the contentsRect ---

        fs = 1                    
        while True:

            f.setPixelSize(fs)
            br =  QFontMetrics(f).boundingRect(self.text())

            if br.height() <= cr.height() and br.width() <= cr.width():
                fs += 1
            else:
                f.setPixelSize(max(fs - 1, 1)) # backtrack
                break  

        #--- update font size ---

        self.setFont(f)   

class resizeImageLabel(QLabel):
    def __init__(self, directory, parent=None):
        super().__init__(parent)
        self.setScaledContents(True)


        img = QPixmap(directory)

        self.imgLabel = imageLabel()
        self.imgLabel.setPixmap(img)

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.grid.addWidget(self.imgLabel)

class imageLabel(dynamicLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScaledContents(True)



    def paintEvent(self, event):
        if self.pixmap():
            pm = self.pixmap()
            originalRatio = pm.width() / pm.height()
            currentRatio = self.width() / self.height()
            if originalRatio != currentRatio:
                qp = QPainter(self)
                pm = self.pixmap().scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                rect = QRect(0, 0, pm.width(), pm.height())
                rect.moveCenter(self.rect().center())
                qp.drawPixmap(rect, pm)
                return
        super().paintEvent(event)

class infoText(QWidget):
    def __init__(self, text, font, parent = None):
        super(infoText, self).__init__(parent)

        self.font = font
        self.setStyleSheet("color: white;")


        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.labelList = []

        for i in range(2):
            label = dynamicLabel(self)
            #label.setText(text)
            label.setFont(self.font)
            label.setAlignment(Qt.AlignCenter)
            self.labelList.append(label)
            self.grid.addWidget(label, i, 0)        

        self.insertText(text)
        #self.grid.setContentsMargins(10, 5, 10, 5)

    def insertText(self, text):
        text = text.split("\n")
        
        for i in range(2):
            if i< len(text):
                self.labelList[i].setText(text[i])
            else:
                self.labelList[i].setText("")
                
        


    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.setRenderHints( QPainter.HighQualityAntialiasing )

        gradient = QLinearGradient(QRectF(self.rect()).topLeft(),QRectF(self.rect()).bottomLeft())
        gradient.setColorAt(0.0, QColor("#150e09"))
        gradient.setColorAt(0.4, QColor("#544538"))

        yMidPoint = QRectF(self.rect()).center().y()

        sideShadows = QLinearGradient(QRectF(self.rect()).left(), yMidPoint, QRectF(self.rect()).right(), yMidPoint)
        sideShadows.setColorAt(0.1, Qt.transparent)
        sideShadows.setColorAt(0.90, Qt.transparent)
        sideShadows.setColorAt(0.0, QColor("#150e09"))
        sideShadows.setColorAt(1.0, QColor("#150e09"))


        
        painter.setBrush(gradient)
        painter.drawRoundedRect(self.rect(), 5.0, 5.0)
        painter.setBrush(sideShadows)
        painter.drawRoundedRect(self.rect(), 5.0, 5.0)

        rectPath = QPainterPath()
        rectPath.addRoundedRect(QRectF(self.rect()), 5.5, 5.5)
        painter.setPen(QPen(QColor("#806752"), 5, Qt.SolidLine,
                                 Qt.RoundCap, Qt.RoundJoin))
        painter.drawPath(rectPath)

class customStepSlider(QWidget):
    def __init__(self, font, info, parent = None):
        super(customStepSlider, self).__init__(parent)

        self.setAttribute(Qt.WA_Hover)
        self.infoConnection = info

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        #self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        self.slider = QRangeSlider(Qt.Orientation.Horizontal)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setMinimum(-2)
        self.slider.setMaximum(10)
        self.slider.setValue((0, 8))
        self.slider.valueChanged.connect(self.updateLabels)

        self.minLabel = QLabel()
        self.minLabel.setText("   0%")
        self.minLabel.setFont(font)
        self.maxLabel = QLabel()
        self.maxLabel.setText("80%")
        self.maxLabel.setFont(font)

        self.titleLabel = dynamicLabel()
        self.titleLabel.setText("Growths Range")
        self.titleLabel.setFont(font)   
        self.titleLabel.setMinSize(20)

        spacer = QSpacerItem(20, 60)

        self.grid.addItem(spacer, 0, 0)

        self.grid.addWidget(self.minLabel, 0, 1, 1, 1)
        self.grid.addWidget(self.slider, 0, 2, 1, 20)
        self.grid.addWidget(self.maxLabel,0 , 23, 1, 1)
        self.grid.addWidget(self.titleLabel, 1, 2, 3, 20, Qt.AlignCenter)


    def setValue(self, value):
        self.slider.setValue((value[0], value[-1]))

    def getValue(self): #this one gets the TRUE value 
        return self.slider.value()  

    def getValues(self):
        return [self.slider.value()[0]*10, self.slider.value()[-1]*10]

    def updateLabels(self):
        minLabel = str(self.slider.value()[0]*10) + "%"
        maxLabel = str(self.slider.value()[-1]*10) + "%"

        minLabel = "  "*(3-len(minLabel)) + minLabel 
        maxLabel = "  "*(3-len(maxLabel)) + maxLabel 

        self.minLabel.setText(minLabel)
        self.maxLabel.setText(maxLabel)

    def event(self, event):
        if event.type() == QEvent.HoverEnter:
            #Send signal
            #print("enter")
            self.infoConnection.changeText("Sets range of growths to \nbe generated while randomizing.")

        elif event.type() == QEvent.HoverLeave:
            #print("leave")
            #Halt signal
            
            pass
        return super().event(event)
        
class critStepSlider(QWidget):
    def __init__(self, font, info, parent = None):
        super(critStepSlider, self).__init__(parent)

        self.setAttribute(Qt.WA_Hover)
        self.infoConnection = info

        self.grid = QGridLayout()
        self.setLayout(self.grid)


        self.slider = QRangeSlider(Qt.Orientation.Horizontal)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setMinimum(2)
        self.slider.setMaximum(20)
        self.slider.setValue((2, 8))
        self.slider.valueChanged.connect(self.updateLabels)

        self.minLabel = QLabel()
        self.minLabel.setText("   5")
        self.minLabel.setFont(font)
        self.maxLabel = QLabel()
        self.maxLabel.setText("40")
        self.maxLabel.setFont(font)

        self.titleLabel = dynamicLabel()
        self.titleLabel.setText("Crit Range")
        self.titleLabel.setFont(font)   
        self.titleLabel.setMinSize(20)

        spacer = QSpacerItem(20, 60)

        self.grid.addItem(spacer, 0, 0)

        self.grid.addWidget(self.minLabel, 0, 1, 1, 1)
        self.grid.addWidget(self.slider, 0, 2, 1, 20)
        self.grid.addWidget(self.maxLabel,0 , 23, 1, 1)
        self.grid.addWidget(self.titleLabel, 1, 2, 3, 20, Qt.AlignCenter)


    def setValue(self, value):
        self.slider.setValue((value[0], value[-1]))

    def getValue(self): #this one gets the TRUE value 
        return self.slider.value()  

    def getValues(self):
        return [self.slider.value()[0]*5, self.slider.value()[-1]*5]

    def updateLabels(self):
        minLabel = str(self.slider.value()[0]*5)
        maxLabel = str(self.slider.value()[-1]*5)

        minLabel = "  "*(2-len(minLabel)) + minLabel 
        maxLabel = "  "*(2-len(maxLabel)) + maxLabel 

        self.minLabel.setText(minLabel)
        self.maxLabel.setText(maxLabel)

    def event(self, event):
        if event.type() == QEvent.HoverEnter:
            #Send signal
            #print("enter")
            self.infoConnection.changeText("Sets range of crit values \nfor weapons with added crit.")

        elif event.type() == QEvent.HoverLeave:
            #print("leave")
            #Halt signal
            
            pass
        return super().event(event)

class aboutWindow(QWidget):
    def __init__(self, font, directory, parent = None):
        super(aboutWindow, self).__init__(parent)
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.setWindowTitle("About")
        self.setWindowIcon(QIcon(directory+"\\randomizer_assets\\infocircle.svg"))

        self.font = font 

        palette = QPalette()
        palette.setColor(QPalette.Text, Qt.white)

        textLabel = self.customTextLabel('''
        <div style = "text-align: center">
        <i style = "font-size:30px">About</i>
        <div style = "font-size: 20px">
        &nbsp;&nbsp;This randomizer is a joint effort by LT and Radd.&nbsp;&nbsp;<br><br>
        &nbsp;For more information (and error reports), <br>
        please visit the <a href = https://github.com/eLTehh/Raddomizer 
        style = "color: #f7f3b9;">Github link here.</a>&nbsp;
        </div>
        <br>
        <br>

        <i style = "font-size:30px">Special Thanks</i>
        </div>
        <div style = "font-size: 20px">
        <ul style = "display:-moz-inline-stack; display: inline-block;
        zoom:1; *display:inline;">
        <li>  &nbsp;Testers: Xylon73, Gammer, Harb1ng3r</li>
        <li> &nbsp;GUI feedback: <a href = https://virize.carrd.co/
        style = "color: #f7f3b9;">Virize</a></li>
        <li>&nbsp;<a href = https://feuniverse.us/t/fe12-nightmare-modules/9525 
        style = "color: #f7f3b9;">FE12 Nightmare Modules</a></li>
        <li>&nbsp;<a href = https://feuniverse.us/t/fe12-growth-cyphers/6380 
        style = "color: #f7f3b9;">FE12 Growth Cyphers</a></li>
        <li>&nbsp;<a href = https://github.com/magical/nlzss/blob/master/lzss3.py 
        style = "color: #f7f3b9;">Nintendo LZ compression</a></li>
        <li>&nbsp;Icons by <a href = https://www.svgrepo.com 
        style = "color: #f7f3b9;">svgrepo.com</a></li>
        </ul>
        </div>
        <div style = "text-align: center">
        <i style = "font-size:17px">Current version: v0.9.6</i>
        </div>

        ''')


        self.grid.addWidget(textLabel, 0,0, Qt.AlignCenter)


    def paintEvent(self, ev):
        painter = QPainter(self)


        painter.setBrush(QColor("#2d637b"))
        painter.drawRect(self.rect())

    def customTextLabel(self, text):
        textLabel = QLabel()
        textLabel.setText(text)
        textLabel.setFont(self.font)
        textLabel.setStyleSheet("color: white;")
        textLabel.setOpenExternalLinks(True)

        self.initBG(textLabel)

        return textLabel

    def initBG(self, widget):
        
        dColor = QColor("#182039")
        dColor.setAlphaF(0.70)


        widget.setAutoFillBackground(True)

        palette = widget.palette()
        palette.setColor(widget.backgroundRole(), dColor)
        widget.setPalette(palette)






def main():
   app = QApplication(sys.argv)
   ex = bigRaddomizer()
   ex.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()
