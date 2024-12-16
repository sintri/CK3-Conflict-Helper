# CK3-Conflict-Helper
<b>WIP Should be relatively stable now.<br>
Variables below #Configurable Variables are designed to be modified.<br>
The program does clear files under outputFolder so be careful where you point it if you change it.</b><br>
Do you hvae more mods than off the shelf compatibility patches can support?<br>
Do you want to make sure you're catching all possible conflicts?<br>
Do you know what you're doing?<br>
If you answered yes to all of the above hopefully this tool can make life easier.<br><br>
<b>Also make sure you know what you're doing, if you don't you'll be wasting alot of time and making things worse.<br></b>
<i>Remember the point is not to merge every file together, it is to resolve object confclits. If objects in a file are naturally going to be overwritten, then a comp patch is not needed for those files.  If the object you want to win has a seperate mod file overwriting it by nature of file name ordering, then you'll need to create a comp patch.</i>
## Description
What this script does do:<br>
- Prepares folders and files for you to make a comp patch out of any modlist
- Points out conflicts with multiple groupings
- Points out pontential issues or redundancies in a mod

What this script doesn't do:<br>
- Resolve conflicts for you
- Guarantee you merged it correctly
- Catch every single conflict, it might be close though
## Outputs
    MyCompPatch - Every detected conflicting file will be placed into this folder along with a descriptor.mod, merge into this to handle basic merge conflicts.
    Mod Folders - Contains files that have conflicts with other mods, grouped by mods
    Conflict Output.txt - List of files that contain overwrites to other fields grouped by field
    Manual Merge Conflict Output.txt - Grouped by conflicting field name
    Manual Merge Conflict Output By File.txt - Grouped by file name, this is the one I would use to do file-file compare
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
3. When done navigate to the ToMerge folder<br>
    It should look something like this:<br>
    ![Sample Output](https://github.com/sintri/CK3-Conflict-Helper/blob/main/HelpFiles/output.PNG)<br>
4. Open up WinMerge (or whatever merge tool you're familar with<br>
    <b>If this is your first time, configure WinMerge for easier use, see below</b><br>
    b. Select the MyCompPatch folder as your first entry.<br>
6. <b>For Each Mod Folder in ToMerge, Do the Following:</b><br>
    b. Set the mod as your second entry.<br>
       ![WinMerge Load](https://github.com/sintri/CK3-Conflict-Helper/blob/main/HelpFiles/winmerge1.PNG)<br>
    c. Go through each file that shows up as conflicted.<br>
       ![WinMerge File List](https://github.com/sintri/CK3-Conflict-Helper/blob/main/HelpFiles/winmerge2.PNG)<br>
       Merge to the best of your knowledge.<br>
       ![WinMerge Difference](https://github.com/sintri/CK3-Conflict-Helper/blob/main/HelpFiles/winmerge3.PNG)<br>
    d. Delete the current mod folder when you're done.<br>
    e. Repeat until there are no more mod folders to merge.<br>
7. Congratulations You're Done, is what I would like to say, but there are technically more things to do. Proceed on if you want.<br>
8. <b>Overtime Steps</b><br>
    You're also allowed to overwrite fields from outside the file.  Skipping this step wouldn't be the end of the world, these conflicts would continue to behave as before.<br>
    Though some mods will definitely be required for you to handle these conflicts or else you might have unexpected behaviour.<br>
    <b>Manual Patching should be done if a file you don't want winning is overwriting a mod you do want winning by virtue of file name load order.</b><br>
    To handle this you'll need to make a file and with the overwrites and have it loaded last to overwrite their overwrites.<br><br>
    A list of these fields have been provided to you in two files, one grouped by the field name the other grouped by the file grouping.<br>
    Manual Merge Conflict Output.txt - Grouped by conflicting field name<br>
    Manual Merge Conflict Output By File.txt - Grouped by file name, this is the one I would use to do file-file compare<br>
9. Go through each file, open up the relevant files and do a manual compare and choose who/which entires should win.<br>
    Afterwards save that file under some ridiculous name so it gets loaded last. ie. zzz_basefilename.txt<br>
    Optionally now you can remove the files involved in this.<br>
    Tip: <i>I would go through folder by folder, double check the file name in Conflict Output.txt, and used Manual Merge Conflcit Output by File.txt as a checklist to remove the group when you're done.</i><br>
10. Repeat until you're done or get bored.<br>
11. <b>Extra Overtime</b><br>
    This tool does not handle GUI files at the moment, those you'll need to merge on your own.<br>
    This tool also doesn't no do yaml, but since that doesn't affect gameplay do it on your own if you want.


## Configuring WinMerge
Click <b>View</b>. Ensure settings are set to these, only showing different items will cut down on the clutter and reduce compares.<br>
![Click View](https://github.com/sintri/CK3-Conflict-Helper/blob/main/HelpFiles/winmergec0.PNG)<br>
Click <b>Edit->Options</b><br>
Click on the <b>Compare</b> tab<br>
Ensure settings are like this. Ignore White spaces cuts down on the comparisons needed. Under <b>Diff algorithm</b>, <b>histogram</b> is generally the most useful for our purposes, though some may be better than others depending on the situation.<br>
![Click Edit](https://github.com/sintri/CK3-Conflict-Helper/blob/main/HelpFiles/winmergec1.PNG)<br>
Click on the <b>Folder</b> tab<br>
Under <b>Automatically expanded subfolders after comparison</b>: click <b>Expand all subfolders</b>.
![Click Edit](https://github.com/sintri/CK3-Conflict-Helper/blob/main/HelpFiles/winmergec2.PNG)<br>
Click <b>OK</b> to finish.
