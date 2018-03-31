"""
# This is the testing ground.
# Develop functions here, but do not leave them here!
# This is a glorified playground to make a mess in!
"""


# Dependencies
import Bracket_Testing as bt
import Database_Management as dm
import Find_Files as ff
import Print_Colour as pc

story_directory = "../Story Segments/"
[files, folders] = ff.discoverFiles(story_directory)
db = dm.getStoryDatabase(files, folders)
for i in db:
    pc.printC(str(db[i]), "WARNING")
    for j in db[i]:
        if j[0][0] == '#':
            code = bt.convertCodeToList(j[0])
            pc.printC(str(code), "OK_GREEN")