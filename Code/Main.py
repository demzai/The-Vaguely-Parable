"""
# Main file
"""


# Dependencies
import Database_Management as dm
import Extract_Narrative as en
import Find_Files as ff
import Print_Colour as pc
import Globals as glbl


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
    glbl.file_locales = ff.discoverFiles(glbl.start_directory)
    [files, folders] = glbl.file_locales
    glbl.database = dm.getStoryDatabase(files, folders)

    # @todo first node = None
    glbl.address_stack.append(getStartNode(files))
    glbl.address_stack.append(getStartNode(files))
    return


def getNarrativeOptions():
    """
    Creates a list of the next addresses accessible to the user
    :return:
    """
    glbl.next_addresses = dm.getFromMap(glbl.address_stack[-1], glbl.database)


def updateAddresses(selection, is_direct_entry=False):
    """
    # Updates the address based on the selection presented
    :param is_direct_entry:
    :param selection:
    :return:
    """
    if is_direct_entry is False:
        if selection not in glbl.next_addresses:
            return False
        else:
            glbl.address_stack.append(glbl.next_addresses[selection])
        return True
    else:
        for i in glbl.next_addresses:
            if selection not in i:
                continue
            else:
                glbl.address_stack.append(glbl.next_addresses[selection])
                return True
    return False


def readNarrative():
    """
    # Reads the narrative pointed to by the current address
    """
    narrative_file = ff.getFileFromCode(glbl.address_stack[-1], glbl.file_locales)
    narrative_text = en.getFileContents(narrative_file)
    for text in narrative_text:
        if text[0] == 'Text' or text[0] == 'Container':
            print(str(text[1]))


if __name__ == '__main__':
    # Begin the game
    initialise()
    readNarrative()

    # Play the game
    while True:
        # Get the users narrative selection
        print(pc.ICyan + '\nPlease select your narrative:\n' + pc.Reset + str(glbl.next_addresses))
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
        print('\nPlease select your narrative:\n' + str(glbl.next_addresses))
        string = input()
        print("")
        if updateAddresses(string, True) is False:
            print('\nERROR - "' + str(string) + '" IS NOT AN OPTION!')
            print('Please try again.')
        else:
            readNarrative()
            getNarrativeOptions()
