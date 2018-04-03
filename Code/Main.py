"""
# Main file
"""


# Dependencies
import Database_Management as dm
import Extract_Narrative as en
import Find_Files as ff
import Print_Colour as pc
import Globals as glbl
import Code_Interpreter as ci


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
    glbl.next_addresses = []
    options = dm.getFromMap(glbl.address_stack[-1], glbl.database)

    for option in options:
        glbl.next_addresses += dm.parseDatabaseEntry(option)

    # glbl.next_addresses = dm.getFromMap(glbl.address_stack[-1], glbl.database)


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
                glbl.address_stack.append(i[0])
                return True
    return False


def readNarrative():
    """
    # Reads the narrative pointed to by the current address
    """
    narrative_file = ff.getFileFromCode(glbl.address_stack[-1], glbl.file_locales)
    narrative_text = en.getFileContents(narrative_file)
    for text in narrative_text:
        if text[0] == 'Text':
            print(str(text[1]))
        elif text[0] == 'Container':
            print(str(ci.parseContainerCode(text[1], text[2])))
        elif text[0] == 'Code' or text[0] == 'Variable':
            ci.interpretCode(text[2][0])
        elif text[0] == 'Segment':
            print('@todo: implement segments!!! - ' + str(text[2]))
            ci.interpretCode(text[2][0])


if __name__ == '__main__':
    import time as t

    # Begin the game
    initialise()
    readNarrative()

    # Skip the narrative a bit:
    choices = ['0/00b', '0/01', '0/02b1', '0/02b2', '0/03b', '0/04', '3/01']
    # Play the game
    for choice in choices:
        # Get the users narrative selection
        getNarrativeOptions()
        print(pc.ICyan + '\nPlease select your narrative:\n' + pc.Reset + str(glbl.next_addresses))
        print(str(choice))
        print("")
        if updateAddresses(choice, True) is False:
            print('\n' + pc.IRed + 'ERROR - "' + str(choice) + '" IS NOT AN OPTION!' + pc.Reset)
            print(pc.IBlue + 'Please try again.' + pc.Reset)
        else:
            readNarrative()
    t.sleep(0.1)

    # Play the game
    while True:
        # Get the users narrative selection
        getNarrativeOptions()
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
    getNarrativeOptions()
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


























