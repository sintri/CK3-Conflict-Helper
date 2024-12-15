# CK3-Conflict-Helper
WIP Use at your own risk<br>
Do you hvae more mods than off the shelf compatibility patches can support?<br>
Do you want to make sure you're catching all possible conflicts?<br>
Do you know what you're doing?<br>
If you answered yes to all of the above hopefully this tool can make life easier.<br>
## Outputs
    Mod Folders - Contains files that have conflicts with other mods, grouped by mods
    Conflict Output.txt - List of files that contain overwrites to other fields grouped by field<br>
    Manual Merge Conflict Output.txt - Grouped by conflicting field name<br>
    Manual Merge Conflict Output By File.txt - Grouped by file name, this is the one I would use to do file-file compare<br>
    Potential Mod Issues Output.txt - Potential duplicates or issues within a mod itself, typically it just means a field has been defined more than once in a file<br>
## Requirements
-CK3 Mods<br>
-Python3 Latest (there's probably dependencies on stuff added in 3.5+ so use the latest if you have it)<br>
-WinMerge (or whate ever compare tool you want)<br>
<p></p>

## Instructions
1. Stick all the mods from your modlist into a directory<br>
2. Open up a command prompt and navigate to your CK3-Conflict-Helper directory<br>
    a. type python3 chm.py "DRIVE:\PATH\TO\WHEREVER\YOU\DUMPED\YOUR\MODLIST"<br>
    b. Press enter and let it run<br>
3. When done navigate to the ToMerge folder<br>
#insert screenshot here<br>
4. Create a base mod folder to hold your comp patch<br>
5. Create or copy over the description.mod provided into your comp patch folder<br>
    b. Modify the name= in description.mod to your comp patch name<br>
6. Open up WinMerge (or whatever merge tool you're familar with<br>
    b. If this is your first time, configure WinMerge for easier use, see below<br>
7. <b>For Each Mod Folder, Do the Following:</b><br>
<i>Tip: Use a comp patch as base, do other comp patches last as they typically contain overwrites that should take precedence over other things</i><br>
8. Open up a mod folder<br>
    b.  Copy contents of the mod folder into your comp patch folder<br>
    c. If no overwrites are present skip to step 10<br>
    d. Skip overwrites if they are present as you'll be using a merge tool for this.<br>
9. Open up the two files in WinMerge<br>
#insert screenshot here<br>
    b. Go through each file present and merge the conflict into your file<br>
        #insert screenshot here<br>
    c. Close out of this WinMerge tab when you are finished<br>
10. Remove the mod directory you have finished merging <br>
11. Go back to step 7 if there are more mods to be merged.<br>
12. Congradulations You're Done, is what I would like to say.  But there are technically more things to do, proceed to step 13 if you want.<br>
13. <b>Overtime Steps</b><br>
    You're also allowed to overwrite fields from outside the file.  Skipping this step wouldn't be the end of the world, these conflicts would continue to behave as before.<br>
    Though some mods will definitely be required for you to handle these conflicts or else you might have unexpected behaviour.<br>
    To handle this you'll need to make a file and with the overwrites and have it loaded last to overwrite their overwrites.<br><br>
    A list of these fields have been provided to you in two files, one grouped by the field name the other grouped by the file grouping.<br>
    Manual Merge Conflict Output.txt - Grouped by conflicting field name<br>
    Manual Merge Conflict Output By File.txt - Grouped by file name, this is the one I would use to do file-file compare<br>
15. More or less go through each file, open up the relevant files and do a manual compare and choose who should win.<br>
    Afterwards save that file under some ridiculous name so it gets loaded last. ie. zzz_basefilename.txt
    Optionally now you can remove the none native file.
17. Repeat until you're done or get bored.

## Configuring up WinMerge
#insert screenshot here<br>
