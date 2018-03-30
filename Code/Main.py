# Dependencies
import Database_Management as dm
import Extract_Narrative as en
import Find_Files as ff


# Global Variables
database = {}
story_directory = "../Story Segments/"
start_address = ""


# Get the start node
def getStartNode(files):
    initial_file = files['Init']
    return (en.getFileContents(initial_file))[0]


def initialise(start_directory=story_directory):
    global database, start_address
    [files, folders] = ff.discoverFiles(start_directory)
    database = dm.getStoryDatabase(files, folders)
    start_address = getStartNode(files)
    return dm.getFromMap(start_address, database)


next_addresses = initialise()
