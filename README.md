# An FE12 randomizer, complete with a GUI and built-in instructions!
## Get the latest version [here!](https://github.com/eLTehh/Raddomizer/releases) 

## Intro
<img src = "readme_images/raddomizer.PNG" width = 25% height = 25%>

Raddomizer is a randomizer for New Mystery of the Emblem. The features are lightweight, and easy to understand. No command line stuff or manual decompression — just pop the unpacked ROM folder into the program and it'll randomize things for you.

This randomizer is a joint effort by LT (me), [Radd](https://twitter.com/Nuthingdude) and Vennobennu. Coding by LT and Vennobennu, documentation by Radd (more info further down in the readme)

It includes a few additional features for an improved gameplay experience, such as removing Prf weapon locks, as well as gendered weapon locks. Also, playable Ballisticians, with their sprites ported over from Shadow Dragon! 

## How to Install
Simply grab the latest release from here: https://github.com/eLTehh/Raddomizer/releases

## Input Format

<img src = "randomizer_assets/rodyfiles.png" width = 50% height = 50%>

You'll want an unpacked New Mystery ROM for this one. Patched ROMs with the English translation should work fine, as well. (Not sure about any gameplay mods; if pointers are switched around, Raddomizer might not randomize the classes properly.)

The input directory selected should look like either of the following:
1. The unpacked ROM
```
.
├── data                  
├── overlay                 
├── arm7.bin                    
├── arm9.bin                    
├── banner.bin                   
├── header.bin
├── y7.bin
└── y9.bin
```
2. The FIRST data folder (not the second one)
```
.
├── 2                  
├── 3                 
├── ascii                    
├── av                    
├── b                   
...(and many more folders, including data)
```


A tool you can use to unpack your ROM is [DSLazy](https://www.romhacking.net/utilities/793/). 

<img src = "randomizer_assets/lukefiles.png" width = 50% height = 50%>

## Putting the randomized files back into the game

<img src = "randomizer_assets/outputtuto.png" width = 50% height = 50%>

Once you've specified your output directory (or if not, Raddomizer will output the files in its own installed directory) and clicked Randomize, your files should be ready.

Make a copy of your unpacked ROM folder, drag the data folder (once again, this is the FIRST data folder, not the second!) inside, and allow it to replace existing files.

Then, pack the folder back into a ROM, and enjoy your randomized New Mystery!

## Sample Screenshots

<img src = "https://media.discordapp.net/attachments/355914063852863489/997082658972631050/unknown.png">

<img src = "https://media.discordapp.net/attachments/822408378130235424/1000330719568085062/unknown.png?width=459&height=669">

<img src = "https://media.discordapp.net/attachments/355914063852863489/997120803164389416/unknown.png">

<img src = "https://media.discordapp.net/attachments/355914063852863489/997122676227321926/unknown.png?width=505&height=669">

<img src = "https://media.discordapp.net/attachments/355914063852863489/997163971683553300/unknown.png">

<img src = "randomizer_assets/EnemyRando.png">

## Known Issues
Class slots (in the Reclass window) seem to fit randomization results, but fliers have been shown to exceed the amount of class slots. Need more testing, unsure if this is the result of changing ROMs in the middle of a run.

If any known issues are found, please send your log alongside the error report!

## Reporting Errors
<img src = "randomizer_assets/error.png" width = 25% height = 25%>
You can use Github's Issues page, or the FEU thread. 
To attach files on Github, you can drag it inside the comment box.

### **Please include the following while submitting your report:**

*If the randomizer ran into an error while randomizing:*
- The error.log file *(in the same directory as Raddomizer)*
- The settings you used to generate this output
- Randomizer version *(found under About)*

*If the error is found during gameplay:*
- Your randomizerLog.txt file
- Your save file (or, at the very least, the chapter the error occurred in)
- Screenshots of the error
- If it's particularly game-breaking, any steps to replicate the error?
- Randomizer version *(found under About)*

*If the randomizer straight up doesn't run*
- Send the error.log file
- Anything else you think is relevant
- (Hopefully this doesn't happen)

## Regarding MacOS support
At the time, MacOS does not support any tools that can unpack/pack DS ROMs. Unarchiver has been tested, and .nds file formats do not seem to be supported anymore. 
Thus, any .nds unpackers would have to be run on a Windows VM, so there isn't much point in deploying a Mac version of Raddomizer.
The issue is being looked into, but not a primary concern right now. Raddomizer will try to support MacOS when it becomes viable.

## Requests for new features
Sure, I'd appreciate your input. However, to set expectations, Raddomizer is something developed in my spare time, so there's no deadline or guarantee they'll be implemented.

In order to prevent myself from getting overwhelmed, my priority is a functional and easy to use randomizer. So bugs will be prioritized over new features.

## How did you do all that? Did you document the information somewhere?
Documentation for FE12 can be found in the [Wiki](https://github.com/eLTehh/Raddomizer/wiki), as well as a few Action Replay codes to help improve the gameplay experience. Once again, special thanks to Radd for documenting FE12's data structure!


## Future Roadmap: Awakening randomizer...?
A bunch of code/decompression algorithms have been written for Awakening, though nothing concrete has been done yet. Most of the code could probably be ported over. Holding off on this right now due to some roadblocks with growths encryption, and unsure if other programmers may be working on an Awakening randomizer as I speak.


## Special Thanks

Testers: Xylon73, Gammer, Harb1ng3r

GUI feedback/advice: [Virize](https://virize.carrd.co/)

[FE12 Nightmare Modules](https://feuniverse.us/t/fe12-nightmare-modules/9525) by a variety of FEU users

[FE12 Growth Cyphers](https://feuniverse.us/t/fe12-growth-cyphers/6380) by Mrkisuke, and the [original documentation](https://forums.serenesforest.net/index.php?/topic/70880-fe12-growth-rate-cipher-documentation/) by SciresM

[Nintendo LZ compression/decompression](https://github.com/magical/nlzss/blob/master/lzss3.py) by magical

Icons by svgrepo.com

 
