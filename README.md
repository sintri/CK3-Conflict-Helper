# CK3-Conflict-Helper
WIP Use at your own risk
## Requirements
-CK3\n<br>
-CK3 Mods<br>
-Python3 Latest (there's probably dependencies on stuff added in 3.5+ so use the latest if you have it)<br>
-WinMerge (or whate ever compare tool you want)<br>
<p></p>

## Instructions
1. Stick all the mods from your modlist into a directory<br>
2. Open up a command prompt and navigate to your CK3-Conflict-Helper directory<br>
2b.type python3 chm.py "DRIVE:\PATH\TO\WHEREVER\YOU\DUMPED\YOUR\MODLIST"<br>
2c.Press enter and let it run<br>
3. When done navigate to the ToMerge folder<br>
#insert screenshot here<br>
4. Create a base mod folder to hold your comp patch<br>
5. Create or copy over the description.mod provided into your comp patch folder<br>
5b. Modify the name= in description.mod to your comp patch name<br>
6. Open up WinMerge (or whatever merge tool you're familar with<br>
6b. If this is your first time, configure WinMerge for easier use, see below<br>
7.<b>For Each Mod Folder, Do the Following:</b><br>
<i>Tip: Do comp patches last as they typically contain overwrites that should take precedence over other things</i><br>
8. Open up mod folder<br>
7b. Copy contents of mod folder into your comp patch folder<br>
7c. If no overwrites are present skip to step 9<br>
7d. Skip overwrites if they are present as you'll be using a merge tool for this.<br>
9. Open up the two files in WinMerge<br>
#insert screenshot here<br>
8b. Go through each file present and merge the conflict into your file<br>
8c. Close out of this WinMerge tab when you are finished<br>
10. Remove the mod directory you have finished merging <br>
11. Continue on to next mod file<br>

## Configuring up WinMerge
#insert screenshot here<br>
