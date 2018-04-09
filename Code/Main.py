"""
# Main file
"""

# Dependencies
import time

import Database_Management as dm
import Extract_Narrative as en
import Find_Files as ff
import Globals as glbl

import Reader


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
    glbl.next_addresses = {}
    options = dm.getFromMap(glbl.address_stack[-1], glbl.database)
    delayed = []

    for option in options:
        new_address = dm.parseDatabaseEntry([options[option], option])
        # print('\t' + pc.IYellow + str(options[option]) + ' - ' + str(new_address) + pc.Reset)  # -------------------

        # Referenced addresses have a lower priority than current addresses, so delay their assimilation
        if len(options[option]) > 1 and options[option][:2] == '#&':
            delayed += [new_address]
            continue

        new_address.update(glbl.next_addresses)
        glbl.next_addresses = new_address

    # Insert the referenced addresses
    for address in delayed:
        address.update(glbl.next_addresses)
        glbl.next_addresses = address

    # Remove select addresses
    for address in glbl.ignore_addresses:
        if isinstance(address, str) or isinstance(address, int) or isinstance(address, float):
            glbl.next_addresses.pop(address, None)
    glbl.ignore_addresses = []  # Reset the ignore list


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


# def readNarrative():
#     """
#     # Reads the narrative pointed to by the current address
#     """
#     narrative_file = ff.getFileFromCode(glbl.address_stack[-1], glbl.file_locales)
#     narrative_text = en.getFileContents(narrative_file)
#     for text in narrative_text:
#         if text[0] == 'Text':
#             print(str(text[1]))
#         elif text[0] == 'Container':
#             print(str(ci.parseContainerCode(text[1], text[2])))
#         elif text[0] == 'Code' or text[0] == 'Variable':
#             ci.interpretCode(text[2][0])
#         elif text[0] == 'Segment':
#             ci.interpretCode(text[2][0])
#     print('')
def readNarrative(reader):
    """
    # Reads the narrative pointed to by the current address
    :param reader: Reader.ReaderObj()
    :return:
    """
    narrative_file = ff.getFileFromCode(glbl.address_stack[-1], glbl.file_locales)
    narrative_text = en.getFileContents(narrative_file)
    reader.stack += narrative_text


def read(reader, text):
    """
    Pass single sentences for processing over to the reader
    :param reader:
    :param text:
    :return:
    """
    to_reader = [['Text', str(text), []]]
    reader.stack += to_reader


def getSelection(preselect=None):
    """
    Select the next narrative path
    :param preselect:
    :return:
    """
    # Get the users selection
    if glbl.do_auto_select is False:
        # print(pc.ICyan + '\nPlease select your narrative:\n' + pc.Reset + str(list(glbl.next_addresses)))
        print('\nPlease select your narrative:\n' + str(list(glbl.next_addresses)))
        if preselect is not None:
            string = preselect
        else:
            string = input()
        print("")

        with open("log_file.txt", "a") as log_file:
            log_file.write('User Select - ' + str(string) + '\n')
    # Or automatically select the next element
    else:
        glbl.do_auto_select = False
        addresses = list(glbl.next_addresses)
        string = addresses[0]
        if 'auto' in addresses:
            string = 'auto'
        with open("log_file.txt", "a") as log_file:
            log_file.write('Auto Select - ' + str(string) + '\n')

    # Return the selection
    return string


def main():
    """
    The main function
    :return:
    """
    # Begin the game
    initialise()
    reader = Reader.ReaderObj()
    readNarrative(reader)
    reader.checkReaderStatus()

    try:
        # Play the game
        while True:
            # Block whilst the narrator reads the script
            # @todo convert to non-blocking method to allow interrupts
            while reader.alive is True:
                reader.checkReaderStatus()
                time.sleep(0.5)

            # Get the users narrative selection
            getNarrativeOptions()

            # Get the users selection
            string = getSelection()

            # Double check that the user hasn't made an error
            if updateAddresses(string, False) is False:
                # print(pc.IRed + 'ERROR - "' + str(string) + '" IS NOT AN OPTION!' + pc.Reset)
                # print(pc.IBlue + 'Please try again.' + pc.Reset)
                read(reader, 'ERROR: "' + str(string) + '" IS NOT AN OPTION!')
                read(reader, 'Please try again.')
                reader.checkReaderStatus()
                with open("log_file.txt", "a") as log_file:
                    log_file.write('User Error - ERROR - "' + str(string) + '" IS NOT AN OPTION!' + '\n')
            else:
                readNarrative(reader)
                reader.checkReaderStatus()
    except Exception as e:
        with open("log_file.txt", "a") as log_file:
            log_file.write('Program Error - {0}'.format(e) + '\n')
        print('{0}'.format(e))
    finally:
        print('AN ERROR HAS OCCURRED! THIS GAME IS NOW CLOSING!')
        time.sleep(5)


if __name__ == '__main__':
    main()
















