"""
# Main file
"""


# Dependencies
import Database_Management as dm
import Extract_Narrative as en
import Find_Files as ff
import Print_Colour as pc
from Globals import start_directory


# Global Variables
database = {}
addresses = ['', '', []]
file_locales = []


# Get the start node
def getStartNode(files):
    """
    # Read the initialisation file
    :param files:
    :return:
    """
    initial_file = files['Init']
    return (en.getFileContents(initial_file))[0][1]


def initialise():
    """
    # Prepare the work environment:
        - create directory database
        - determine previous, start and next addresses
    """
    global database, addresses, file_locales
    file_locales = ff.discoverFiles(start_directory)
    [files, folders] = file_locales
    database = dm.getStoryDatabase(files, folders)
    addresses[0] = getStartNode(files)
    addresses[1] = addresses[0]
    addresses[2] = dm.getFromMap(addresses[1], database)
    return


def updateAddresses(selection, is_direct_entry=False):
    """
    # Updates the address based on the selection presented
    :param is_direct_entry:
    :param selection:
    :return:
    """
    if is_direct_entry is False:
        if selection not in addresses[2]:
            return False
        else:
            addresses[0] = addresses[1]
            addresses[1] = addresses[2][selection]
            addresses[2] = dm.getFromMap(addresses[1], database)
        return True
    else:
        for i in addresses[2]:
            if selection not in i:
                continue
            else:
                addresses[0] = addresses[1]
                addresses[1] = selection
                addresses[2] = dm.getFromMap(addresses[1], database)
                return True
    return False


def readNarrative():
    """
    # Reads the narrative pointed to by the current address
    """
    narrative_file = ff.getFileFromCode(addresses[1], file_locales)
    narrative_text = en.getFileContents(narrative_file)
    for text in narrative_text:
        if text[0] == 'Text' or text[0] == 'Container':
            print(str(text[1]))


if __name__ == '__main__':
    initialise()
    readNarrative()
    while True:
        print(pc.ICyan + '\nPlease select your narrative:\n' + pc.Reset + str(addresses[2]))
        string = input()
        print("")
        if updateAddresses(string, True) is False:
            print('\n' + pc.IRed + 'ERROR - "' + str(string) + '" IS NOT AN OPTION!' + pc.Reset)
            print(pc.IBlue + 'Please try again.' + pc.Reset)
        else:
            readNarrative()
else:
    initialise()
    readNarrative()
    while True:
        print('\nPlease select your narrative:\n' + str(addresses[2]))
        string = input()
        print("")
        if updateAddresses(string, True) is False:
            print('\nERROR - "' + str(string) + '" IS NOT AN OPTION!')
            print('Please try again.')
        else:
            readNarrative()
