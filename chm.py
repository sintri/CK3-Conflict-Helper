import os
import sys
import re
import math
from tqdm import tqdm
import time
from pathlib import Path
import shutil

# Configurable Variables
setupForMerging = True # If False will only print out output files if you only wanted to know which files are conflicting
setupMergeFolderPath = "MyCompPatch" # Created Folder Name, Change if you want
setupMergeFolderName = "My Comptability Mod" # Created Folder Description, Change if you want
ignoreSameModMerges = True # Don't output to Manual Merge Conflict is conflicts all from same mod, trust mod maker knew what they were doing
outputFolder = "ToMerge" # This is the output folder, it will also be cleared every time so you shouldn't randomly replace this
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
    "common\\on_action", # On actions append, other things overwrite, generally ok but remove if you need to check
    "gfx\\coat_of_arms\\colored_emblems", 
    "gfx\\court_scene\\scene_settings", # Keyed by name per file, shouldn't have conflicts™
    "history\\characters",
    "history\\cultures",
    "history\\titles",
    "history\\provinces",
]
# For things are actually unique depending on which depth is being set
variableSpecialBraceCount = {
    "special_genes": 3,
    "age_presets": 2,
    "morph_genes": 2,
    "accessory_genes": 2,
    "colors": 2
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
    "vbox": "name"
}

#=== DO NOT TOUCH BELOW THIS LINE UNLESS YOU KNOW WHAT YOU'RE DOING ===#
# Declarations
conflictList = {}
issuesList = {}
manualMergeRequiredList = {}
manualMergeRequiredListByFile = []
malformedOpeningFileList = []
malformedClosingFileList = []
finalFileList = []
finalManualFileList = []
modInfo = {}
patternComment = re.compile("^\s*#.*")
patternOpen = re.compile(r"\s*=\s*{")
patternSet = re.compile(r"\s*=")
outputFolder = ".\\"+outputFolder
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
    if setupForMerging:
        if os.path.exists(setupMergeFolderPath):
            pbar.close()
            print("\nPrexisting Merge folder detected, please move or delete old merge folder "+setupMergeFolderPath+"\n")
            print("This is in case you accidently overwrite a working copy\n")
            exit()
    
    for dirPath, subdirs, files in os.walk(rootDir):
        if dirPath[len(rootDir):].count(os.sep) == 1:
            baseDir = os.path.relpath(dirPath, rootDir).strip()
        elif dirPath[len(rootDir):].count(os.sep) == 2:
            # Skip .git
            if os.path.relpath(dirPath, rootDir).replace(baseDir+"\\",'') == ".git":
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
            # TXT File: Parse for Conflicts, can't do GUIs without more robust parsing
            if file.endswith(".txt"):
                f = open(os.path.join(dirPath,file), "r",encoding='utf-8-sig', errors='ignore')
                braceCount = 0
                braceCountNeeded = 1
                lineCount = 0
                variableName = ""
                for x in f:
                    lineCount+=1
                    insertRecord = False
                    # Check and Skip Commented Out Lines
                    result = re.search(patternComment, x)
                    if (result):
                        continue
                    # Check for Brace Start
                    result = getTotalCount("{",x) # Cause some people can't be trusted with proper formatting
                    if result:
                        braceCount+=result
                        #print("--->open:"+str(braceCount)+x) # BRACE DEBUG
                        if braceCount == 1: # Parent Start
                            if re.search(patternOpen,x):
                                variableName = x[:re.search(patternOpen,x).start()].lstrip()
                                if variableName in variableSpecialBraceCount:
                                    # Special Case, Dive Deeper
                                    braceCountNeeded = variableSpecialBraceCount[variableName]
                            #else: # Shouldn't Happen TM
                                #print("Shouldn't happen:"+os.path.join(dirPath,file)+":Line:"+str(lineCount))
                        elif braceCount > 1 and re.search(patternOpen,x):
                            variableName += "->"+x[:re.search(patternOpen,x).start()].lstrip()
                        if (braceCount == braceCountNeeded and 
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
                        braceCount-=result
                        #print("<---close:"+str(braceCount)+x) # BRACE DEBUG
                    if braceCount <= 0:
                        braceCountNeeded = 1;
                        if braceCount < 0:
                            braceCount = 0; # Power through
                            if not recordedFile:
                                malformedClosingFileList.append(os.path.join(dirPath,file))
                                recordedFile = True
                if braceCount > 0:
                    malformedOpeningFileList.append(os.path.join(dirPath,file))
                
    pbar.refresh()
    pbar.close()

    print("Creating Outputs Files")
    # Output Conflicts
    print("-Outputting Mod Conflicts")
    pbar = tqdm(total=len(conflictList))
    if setupForMerging:
        # Create Merge Mod Base Folder
        makePath = Path(setupMergeFolderPath)
        makePath.mkdir(parents=True, exist_ok=True)
        # Clear Merge Folder
        for fileName in os.listdir(outputFolder):
            file_path = os.path.join(outputFolder, fileName)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    file = open(outputFolder+'\\Conflict Output.txt', 'w', encoding='utf-8-sig')
    prevRelPath = ""
    curRelPath = ""
    prevFile = ""
    issuesListTotalCount = 0
    for key in conflictList:
        pbar.update(1)
        requireManualChecks = False
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
                if setupForMerging and not (sum((file.count(modFolderName) for file in conflictList[key])) == len(conflictList[key])):
                    # Second Part of the logic ignores files if the conflicted object all came from the same mod since hopefully they knew
                    # what they were doing when they made the mod
                    # Create Merge Directory
                    sanitizedModName = sanitizeFolderName(modInfo[modFolderName].strip())
                    modFilePath = outputFolder+baseModFolder.replace(modFolderName,sanitizedModName) # Mod to compare
                    mergeModPath = setupMergeFolderPath+baseModFolder.replace(modFolderName,"") # Mod to merge into
                    baseModFolder = modFilePath[:modFilePath.rfind("\\")].replace("|","") # Mod to compare
                    mergeModPath = mergeModPath[:mergeModPath.rfind("\\")].replace("|","") # Mod to merge into
                    makePath = Path(baseModFolder)
                    makePath.mkdir(parents=True, exist_ok=True)
                    checkExists = Path(modFilePath)
                    if prevFile == "":
                        prevFile = fileName[fileName.rfind("\\"):]
                    if prevFile != fileName[fileName.rfind("\\"):]:
                        requireManualChecks = True
                        prevFile = fileName[fileName.rfind("\\"):]
                    if not checkExists.is_file():
                        shutil.copy(fileName, baseModFolder)
                        makePath = Path(mergeModPath)
                        makePath.mkdir(parents=True, exist_ok=True)
                        shutil.copy(fileName, mergeModPath)
                # Output Mod Path
                file.write("  "+fileName+"\n")
                if fileName not in finalFileList:
                    finalFileList.append(fileName)
            file.write("\n")
            if requireManualChecks:
                manualMergeRequiredList[key] = conflictList[key]
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
    file = open(outputFolder+'\\Potential Mod Issues Output.txt', 'w', encoding='utf-8-sig')
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
    
    if setupForMerging:
        # Create Mod Description File
        file = open(setupMergeFolderPath+'\\descriptor.mod', 'w', encoding='utf-8-sig')
        file.write("version=\"1.0.0\"")
        file.write("tags={")
        file.write("}")
        file.write("name=\""+setupMergeFolderName+"\"")
        file.write("supported_version=\"1.14.*\"")
        file.close()
        # Create Merging Conflict Info File
        print("-Outputting Files That May Require Manual Merging")
        pbar = tqdm(total=len(manualMergeRequiredList))
        file = open(outputFolder+'\\Manual Merge Conflict Output.txt', 'w', encoding='utf-8-sig')
        file.write("These files may require manual merging and patching.\n")
        file.write("Field Count: "+str(len(manualMergeRequiredList))+"\n")
        for key in manualMergeRequiredList:
            pbar.update(1)
            listIndex = -1
            # Print out conflict
            file.write("  "+key+"\n")
            for fileName in manualMergeRequiredList[key]:
                # Create File Groupings here for use later.
                if listIndex == -1:
                    for idx, fileList in enumerate(manualMergeRequiredListByFile):
                        if fileName in fileList:
                            listIndex = idx
                else:
                    if fileName not in manualMergeRequiredListByFile[listIndex]:
                        manualMergeRequiredListByFile[listIndex].append(fileName)
                if listIndex == -1:
                    manualMergeRequiredListByFile.append([fileName])
                    listIndex = len(manualMergeRequiredListByFile)-1
                # Parse Mod Name
                baseModFolder = fileName.replace(rootDir, '')
                modFolderName = baseModFolder.split("\\")[1]
                file.write("  └ "+modInfo[modFolderName])
                # Output Mod Path
                file.write("  "+fileName+"\n")
            file.write("\n")
            if fileName not in finalManualFileList:
                finalManualFileList.append(fileName)
        file.write("\nFile List "+str(len(finalManualFileList))+"\n")
        file.close()
        
        # Manual Conflicts Grouped by File
        file = open(outputFolder+'\\Manual Merge Conflict Output By File.txt', 'w', encoding='utf-8-sig')
        file.write("These files may require manual merging and patching.\n")
        file.write("Group Count: "+str(len(manualMergeRequiredListByFile))+"\n")
        for fileList  in manualMergeRequiredListByFile:
            # Parse Mod Name
            #baseModFolder = fileList[0].replace(rootDir, '')
            #modFolderName = baseModFolder.split("\\")[1]
            #if sum((file.count(modFolderName) for file in fileList)) == len(fileList):
                #continue
            file.write("{\n")
            dupCheck = []
            for fileName in fileList:
                baseModFolder = fileName.replace(rootDir,'')
                modFolderName = baseModFolder.split("\\")[1]
                modFilePath = baseModFolder.replace(modFolderName,setupMergeFolderPath)
                modFilePath = modFilePath.replace("\\.\\","")
                if modFilePath not in dupCheck:
                    file.write("  "+modFilePath+"\n")
                    dupCheck.append(modFilePath)
            file.write("}\n")
        file.close()
        
        pbar.refresh()
        pbar.close()
        
    print("Done.")

if __name__ == '__main__':
    main()