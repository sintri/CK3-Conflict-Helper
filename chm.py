import os
import sys
import re
import math
from tqdm import tqdm
import time
from pathlib import Path
import shutil

# Configurable Variables
setupMergeFolderPath = "MyCompPatch" # Created Folder Name, Change if you want
setupMergeModDesc = "My Comptability Mod" # Created Folder Description, Change if you want
versionString = "1.0.0"
supportVersionString = "1.14.*"
makeEmptyOverwriteFile = False # Creates a empty zzzzz_foldername.txt file for you to merge into
# For when you really don't care about checking this field
ignoreFields = []
# I'm not touching these, generally assume they're fine if you have comp patches since they're alot of work
# Remove ones you do care about
ignoreFolders = [
    "common\\bookmark_portraits", 
    "common\\coat_of_arms\\coat_of_arms", 
    "common\\culture\\cultures",
    #"common\\culture\\eras", # This is short, also one of the mods was overwriting something they shouldn't
    "common\\culture\\innovations",
    "common\\culture\\name_lists",
    "common\\culture\\pillars",
    "common\\culture\\traditions",
    "common\\dna_data",
    "common\\defines", # TODO: Script is not set up to handle individual defines so will always list as conflict if in same object, there may be actual conflicting defines though
    "common\\dynasties", 
    "common\\ethnicities", 
    "common\\men_at_arms_types", # Can probably ignore, typically aren't overwritten
    "common\\modifier_definition_formats", # Can probably ignore, typically aren't overwritten between mods
    "common\\modifiers", # Can probably ignore, typically aren't overwritten between mods
    "common\\named_colors", # If you really care about color define overwrites, remove
    #"common\\on_action", # This appends, but also some mod overwriting the vanilla so delete this folder if you sure you're good
    "common\\religion\\religions", #lots of overwrites here, remove if you need to see it
    #"common\\scripted_values", # While script is not set up to handle individual defines it will still detect object overrides so should still check
    "gfx\\coat_of_arms\\colored_emblems", 
    "gfx\\court_scene\\scene_settings", # Keyed by name per file, shouldn't have conflicts™
    #"history\\characters", # Apparently I need this one
    "history\\cultures",
    "history\\titles",
    "history\\provinces",
]
# For things are actually unique depending on which depth is being set
variableSpecialobjectDepth = {
    "special_genes": 3,
    "age_presets": 2,
    "morph_genes": 2,
    "accessory_genes": 2,
    "colors": 2,
    "doctrine_core_tenets": 2, # Pretty sure this appoends
}
# For fields that are keyed based on another id field
variableSpecialUniqueCheck = {
    "pattern_textures": "name",
    "variation": "name",
    "layer": "name",
    "object": "name",
    "posteffect_values": "name",
    "posteffect_volume": "name",
    "colorbalance": "name",
    "pattern_layout": "name",
    "category": "name",
    "macro": "definition",
    "war": "name",
    "widget": "name",
    "window": "name",
    "texticon": "icon",
    "vbox": "name",
    "game_object_locator": "name"
}

#=== DO NOT TOUCH BELOW THIS LINE UNLESS YOU KNOW WHAT YOU'RE DOING ===#
# Declarations
conflictList = {}
issuesList = {}
forceInclude = []
malformedOpeningFileList = []
malformedClosingFileList = []
finalFileList = []
modInfo = {}
patternComment = re.compile("^\s*#.*")
patternOpen = re.compile(r"\s*=\s*{")
patternSet = re.compile(r"\s*=")
setupMergeFolderPath = ".\\"+setupMergeFolderPath

def sanitizeFolderName(folderName):
    disallowedFolderChars = ["/","<",">",":","\"","\\","|","?","*"]
    for stripChar in disallowedFolderChars:
        folderName = folderName.replace(stripChar, "")
    return folderName
    

def getTotalCount(checkChar, checkString):
    count = 0
    ignorePound = False
    for thisChar in checkString:
        if thisChar == '"':
            if ignorePound:
                ignorePound = False
            else:
                ignorePound = True
        if not ignorePound and thisChar == '#':
            return count
        if thisChar == checkChar:
            count+=1
    return count

def main():
    if len(sys.argv) == 0:
        print("Pass in base directory as first argument");
        exit

    rootDir = sys.argv[1]
    totalFileCount = sum([len(files) for r, d, files in os.walk(rootDir)])
    print("Processing "+str(totalFileCount)+" Files")
    pbar = tqdm(total=totalFileCount)
    fileOutputBuffer = {}
    if os.path.exists(setupMergeFolderPath):
        pbar.close()
        print("\nPrexisting Merge folder detected, please move or delete old merge folder "+setupMergeFolderPath+"\n")
        print("This is to prevent accidently overwrite a working copy\n")
        exit()
    
    for dirPath, subdirs, files in os.walk(rootDir):
        if dirPath[len(rootDir):].count(os.sep) == 1:
            baseDir = os.path.relpath(dirPath, rootDir).strip()
        elif dirPath[len(rootDir):].count(os.sep) == 2:
            # Skip .git
            if os.path.relpath(dirPath, rootDir).replace(baseDir+"\\",'') == ".git":
                continue
            # Skip src, who's including this anyways
            if os.path.relpath(dirPath, rootDir).replace(baseDir+"\\",'') == "src":
                continue
        for file in files:
            recordedFile = False
            pbar.update(1)
            # Skip Files in Folders We Don't Care About
            relPath = os.path.relpath(dirPath, rootDir).strip()
            relPathMod = relPath.replace(baseDir+"\\",'')
            if relPathMod in ignoreFolders:
                continue
            # .MOD File: Store Mod Name
            if file.endswith(".mod"):
                f = open(os.path.join(dirPath,file), "r",encoding='utf-8-sig', errors='ignore')
                for x in f:
                    if "name=" in x:
                        modInfo[baseDir] = x.replace("\"","")[x.index("\""):]
            # TODO: Properly parse guis, for now just spit out files that are the same name
            if file.endswith(".gui"):
                key = file+" --- "+relPathMod
                value = os.path.join(dirPath,file)
                if (not conflictList.get(key)):
                    conflictList[key] = [value]
                    issuesList[key] = [value]
                else:
                    if not value in conflictList.get(key):
                        conflictList.get(key).append(value)
                    else:
                        issuesList.get(key).append(value)
                if (not fileOutputBuffer.get(key)):
                    fileOutputBuffer[key] = []
                objectString = ""
                f = open(os.path.join(dirPath,file), "r",encoding='utf-8-sig', errors='ignore')
                for x in f:
                    objectString += x
                fileOutputBuffer.get(key).append([value,objectString])
            # TXT File: Parse for Conflicts
            if file.endswith(".txt"):
                f = open(os.path.join(dirPath,file), "r",encoding='utf-8-sig', errors='ignore')
                objectDepth = 0
                objectDepthNeeded = 1
                lineCount = 0
                variableName = ""
                objectKeys = []
                objectString = ""
                localDefines = ""
                insertLocalDefines = True
                for x in f:
                    lineCount+=1
                    insertRecord = False
                    objectString += x
                    
                    # Check and Skip Commented Out Lines
                    commentFlag = re.search(patternComment, x)
                    if (commentFlag):
                        continue
                        
                    # Store local defines
                    if x.startswith("@") or x.startswith("namespace"):
                        localDefines += x
                    
                    # Object might not be overwritten but still need re-indexing if occurs at this depth
                    if objectDepth== 1 and "index =" in x and not "texture_index =" in x:
                        if key not in forceInclude:
                            forceInclude.append(key)
                        
                    # Check for Brace Start
                    result = getTotalCount("{",x) # Cause some people can't be trusted with proper formatting
                    if result:
                        if objectDepth == 0:
                            if insertLocalDefines:
                                if len(localDefines):
                                    objectString = localDefines
                                    insertLocalDefines = False
                            else:
                                objectString = ""
                            objectString += x
                        objectDepth+=result
                        #print("--->open:"+str(objectDepth)+x) # BRACE DEBUG
                        if objectDepth == 1: # Parent Start
                            if re.search(patternOpen,x):
                                variableName = x[:re.search(patternOpen,x).start()].lstrip()
                                if variableName in variableSpecialobjectDepth:
                                    # Special Case, Dive Deeper
                                    objectDepthNeeded = variableSpecialobjectDepth[variableName]
                            #else: # Shouldn't Happen TM
                                #print("Shouldn't happen:"+os.path.join(dirPath,file)+":Line:"+str(lineCount))
                        elif objectDepth > 1 and re.search(patternOpen,x):
                            variableName += "->"+x[:re.search(patternOpen,x).start()].lstrip()
                        if (objectDepth == objectDepthNeeded and 
                        variableName not in ignoreFields and 
                        variableName not in variableSpecialUniqueCheck):
                            insertRecord = True
                            # Found what we needed, reset
                    else:
                        result = getTotalCount("=",x)
                        if result:
                            variableName = x[:re.search(patternSet,x).start()].lstrip()
                            
                    # Check for Special Cases
                    if variableName in variableSpecialUniqueCheck:
                        if variableSpecialUniqueCheck[variableName] in x:
                            appendVar = x.split("=")
                            variableName += " - "+appendVar[1].replace("\"","").strip()
                            insertRecord = True
                            
                    # Check if we need to insert recrod
                    if insertRecord:
                        #print(variableName) # BRACE DEBUG
                        key = variableName+" --- "+relPathMod
                        objectKeys.append(key)
                        value = os.path.join(dirPath,file)
                        if (not conflictList.get(key)):
                            conflictList[key] = [value]
                            issuesList[key] = [value]
                        else:
                            if not value in conflictList.get(key):
                                conflictList.get(key).append(value)
                            else:
                                issuesList.get(key).append(value)
                                
                    # Check for brace end
                    result = getTotalCount("}",x) # Cause some people can't be trusted with proper formatting
                    if result:
                        objectDepth-=result
                        #print("<---close:"+str(objectDepth)+x) # BRACE DEBUG
                    if objectDepth <= 0:
                        if len(objectKeys) != 0:
                            for key in objectKeys:
                                if (not fileOutputBuffer.get(key)):
                                    fileOutputBuffer[key] = []
                                fileOutputBuffer.get(key).append([value,objectString])
                                objectKeys = []
                        objectDepthNeeded = 1;
                        if objectDepth < 0:
                            objectDepth = 0; # Power through
                            if not recordedFile:
                                malformedClosingFileList.append(os.path.join(dirPath,file))
                                recordedFile = True
                                
                if objectDepth > 0:
                    malformedOpeningFileList.append(os.path.join(dirPath,file))
    pbar.refresh()
    pbar.close()
    
    print("Create Merge Files")
    # Output Conflicts
    # Create Merge Mod Base Folder
    makePath = Path(setupMergeFolderPath)
    makePath.mkdir(parents=True, exist_ok=True)
    #Create Mod Description File
    file = open(setupMergeFolderPath+'\\descriptor.mod', 'w', encoding='utf-8-sig')
    file.write("version=\""+versionString+"\"\n")
    file.write("tags={\n")
    file.write("}\n")
    file.write("name=\""+setupMergeModDesc+"\"\n")
    file.write("supported_version=\""+supportVersionString+"\"")
    file.close()
    # Create Merge Files
    print("-Merging Files")
    pbar = tqdm(total=len(conflictList))
    for key in conflictList:
        pbar.update(1)
        if len(conflictList[key]) > 1 or key in forceInclude:
            #print(conflictList[key])
            if key in fileOutputBuffer:
                prevModName = ""
                prevModContents = ""
                if key in forceInclude:
                    notSameFile = True
                    notSameMod = True
                else:
                    notSameFile = False
                    notSameMod = False
                # Check if conflicts are all from the same mod or have same contents
                for writeOut in fileOutputBuffer[key]:
                    #Parse Mod Name
                    if prevModName == "":
                        prevModName = writeOut[0].replace(rootDir, '').split("\\",1)[1].split("\\",1)[0]
                    else:
                        if prevModName != writeOut[0].replace(rootDir, '').split("\\",1)[1].split("\\",1)[0]:
                            notSameMod = True
                    #Parse Mod Contents
                    if prevModContents == "":
                        prevModContents = writeOut[1]
                    else:
                        if prevModContents != writeOut[1]:
                            notSameFile = True
                # Only output files with different contents from different mods
                if notSameFile and notSameMod:
                    for writeOut in fileOutputBuffer[key]:
                        #Parse Mod Name
                        baseModFolder = writeOut[0].replace(rootDir, '').split("\\",1)[1]
                        makeModFolder = baseModFolder.split("\\",1)[1]
                        makeModFolder = setupMergeFolderPath+"\\"+makeModFolder[:makeModFolder.rfind("\\")]
                        makePath = Path(makeModFolder)
                        makePath.mkdir(parents=True, exist_ok=True)
                        makeFile = baseModFolder.split("\\",1)[0]+" "+baseModFolder[baseModFolder.rfind("\\")+1:]
                        if os.path.isfile(makeModFolder+"\\"+makeFile):
                            with open(makeModFolder+"\\"+makeFile, encoding='utf-8-sig') as fileCheck:
                                if writeOut[1] in fileCheck.read():
                                    continue
                        file = open(makeModFolder+"\\"+makeFile, 'a', encoding='utf-8-sig')
                        file.write(writeOut[1]+"\n")
                        file.close()
                        if makeEmptyOverwriteFile:
                            file = open(makeModFolder+"\\zzzzz_"+makeModFolder[makeModFolder.rfind("\\")+1:]+".txt", 'w', encoding='utf-8-sig')
                        file.close()
    pbar.refresh()
    pbar.close()

    print("Create Outputs Files")
    # Output Conflicts
    print("-Outputting Mod Conflicts")
    pbar = tqdm(total=len(conflictList))
    file = open(setupMergeFolderPath+'\\Conflict Output.txt', 'w', encoding='utf-8-sig')
    prevRelPath = ""
    curRelPath = ""
    prevFile = ""
    issuesListTotalCount = 0
    for key in conflictList:
        pbar.update(1)
        prevFile = ""
        # Do issuesList count here for prgoress bar later
        if len(issuesList[key]) > 1:
            issuesListTotalCount+=1
        # Check if this field actually has conflicts
        if len(conflictList[key]) > 1:
            # Create a header so we can collapse the section
            curRelPath = key.split("---")[1].strip()+"\n"
            if curRelPath != prevRelPath:
                if prevRelPath != "":
                    file.write("}\n")
                file.write(curRelPath)
                file.write("{\n")
                prevRelPath = curRelPath
            # Print out conflict
            file.write("  "+key+"\n")
            for fileName in conflictList[key]:
                # Parse Mod Name
                baseModFolder = fileName.replace(rootDir, '')
                modFolderName = baseModFolder.split("\\")[1]
                file.write("  └ "+modInfo[modFolderName])
                # Output Mod Path
                file.write("  "+fileName+"\n")
                if fileName not in finalFileList:
                    finalFileList.append(fileName)
            file.write("\n")
    file.write("}\n")
    # Print Conflict Count
    file.write("Total conflict file count: "+str(len(finalFileList))+"\n")
    file.write("{\n")
    for fileName in finalFileList:
        file.write("  "+fileName+"\n")
    file.write("}\n")
    file.close()
    pbar.refresh()
    pbar.close()
    
    # Probable Errors Within the Mod Itself
    print("-Outputting Potential Mod Issues")
    pbar = tqdm(total=issuesListTotalCount)
    file = open(setupMergeFolderPath+'\\Potential Mod Issues Output.txt', 'w', encoding='utf-8-sig')
    prevRelPath = ""
    curRelPath = ""
    if len(malformedOpeningFileList):
        file.write("Too many opening brackets\n")
        file.write("{\n")
        for fileName  in malformedOpeningFileList:
            file.write("  "+fileName+"\n")
        file.write("}\n\n")
    if len(malformedClosingFileList):
        file.write("Too many closing brackets\n")
        file.write("{\n")
        for fileName  in malformedClosingFileList:
            file.write("  "+fileName+"\n")
        file.write("}\n\n")
    file.write("Potential Duplicate or Other Issues Entries\n")
    for key in issuesList:
        if len(issuesList[key]) > 1:
            pbar.update(1)
            # Create a header so we can collapse the section
            curRelPath = key.split("---")[1].strip()+"\n"
            if curRelPath != prevRelPath:
                if prevRelPath != "":
                    file.write("}\n")
                file.write(curRelPath)
                file.write("{\n")
                prevRelPath = curRelPath
            # Print out conflict
            file.write("  "+key+"\n")
            for fileName in issuesList[key]:
                # Parse Mod Name
                baseModFolder = fileName.replace(rootDir, '')
                modFolderName = baseModFolder.split("\\")[1]
                file.write("  └ "+modInfo[modFolderName])
                # Output Mod Path
                file.write("  "+fileName+"\n")
            file.write("\n")
    file.write("}\n")
    file.close()
    pbar.refresh()
    pbar.close()
    
    print("Done.")

if __name__ == '__main__':
    main()