# CK3-Conflict-Helper
<b>WIP Should be relatively stable now, rework done should make the process far easier<br>
Variables below #Configurable Variables are designed to be modified.<br></b>
Do you have more mods than off the shelf compatibility patches can support?<br>
Do you want to make sure you're catching all possible conflicts?<br>
Do you know what you're doing?<br>
If you answered yes to all of the above hopefully this tool can make life easier.<br><br>
<b>Also make sure you know what you're doing, if you don't you'll be wasting alot of time and making things worse.<br></b>
## Description
What this script does do:<br>
- Prepares folders and files for you to make a comp patch out of any modlist
- Points out conflicts by overwrite groupings
- Points out pontential issues or redundancies in a mod
What this script doesn't do:<br>
- Resolve conflicts for you
- Guarantee you merged it correctly
- Catch every single conflict, it might be close though

## Outputs
    MyCompPatch - Every detected conflicting file will be placed into this folder along with a descriptor.mod, merge into this to handle basic merge conflicts.
    Mod Folders - Contains files that have conflicts with other mods, grouped by mods
    Conflict Output.txt - List of files that contain overwrites to other fields grouped by field
    Potential Mod Issues Output.txt - Potential duplicates or issues within a mod itself, typically it just means a field has been defined more than once in a file
    
## Requirements
    -CK3 Mods
    -Python3 Latest (there's probably dependencies on stuff added in 3.5+ so use the latest if you have it)
    -WinMerge (or whate ever compare tool you want)

## Instructions
1. Stick all the mods from your modlist into a directory<br>
2. Open up a command prompt and navigate to your CK3-Conflict-Helper directory<br>
    a. type python3 chm.py "DRIVE:\PATH\TO\WHEREVER\YOU\DUMPED\YOUR\MODLIST"<br>
    b. Press enter and let it run<br>
    ![Sample Run](https://github.com/sintri/CK3-Conflict-Helper/blob/main/HelpFiles/cmd1.PNG)<br>
3. When done navigate to the MyCompPatch folder<br>
    ![Sample Run](https://github.com/sintri/CK3-Conflict-Helper/blob/main/HelpFiles/output.PNG)<br>
4. Open up WinMerge (or whatever merge tool you're familar with<br>
    <b>If this is your first time, configure WinMerge for easier use, see below</b><br>
5. <b>For Each Mod File, start with a compatibility patch as a base as that'll be far less work and merge all conflicts</b><br>
    Consult the Conflict Output.txt if you need help with which fields are being overwritten by which mods as well which mods are which.<br>
    Also note that some files may not neccessarily require merging (like in the instance of Mod1, Mod2, Mod1 + Mod2 Comp Patch are the only files in conflict) or are the same file contents .<br>
    For these you can safely remove all files and let load ordering take care of it.<br>
    ![Sample Run](https://github.com/sintri/CK3-Conflict-Helper/blob/main/HelpFiles/output2.PNG)<br>
    a. Delete the finished mod files when you're done.<br>
    b. Repeat until you have merged every file in every folder.<br>
6. <b>Overtime</b><br>
    This tool also doesn't no do yaml, but since that doesn't affect gameplay do it on your own if you want.

## Configuring WinMerge
Click <b>View</b>. Ensure settings are set to these, only showing different items will cut down on the clutter and reduce compares.<br>
![Click View](https://github.com/sintri/CK3-Conflict-Helper/blob/main/HelpFiles/winmergec0.PNG)<br>
Click <b>Edit->Options</b><br>
Click on the <b>Compare</b> tab<br>
Ensure settings are like this. Ignore White spaces cuts down on the comparisons needed. Under <b>Diff algorithm</b>, <b>patience</b> is generally the most useful for our purposes, though some may be better than others depending on the situation.<br>
![Click Edit](https://github.com/sintri/CK3-Conflict-Helper/blob/main/HelpFiles/winmergec1.PNG)<br>
Click on the <b>Folder</b> tab<br>
Under <b>Automatically expanded subfolders after comparison</b>: click <b>Expand all subfolders</b>.
![Click Edit](https://github.com/sintri/CK3-Conflict-Helper/blob/main/HelpFiles/winmergec2.PNG)<br>
Click <b>OK</b> to finish.
