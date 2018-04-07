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
            # print(str(text))  # ------------------------------------------------------------------------------------
            print(str(ci.parseContainerCode(text[1], text[2])))
        elif text[0] == 'Code' or text[0] == 'Variable':
            ci.interpretCode(text[2][0])
        elif text[0] == 'Segment':
            ci.interpretCode(text[2][0])
    print('')


def main():
    """
    The main function
    :return:
    """
    # Begin the game
    initialise()
    # print(str(glbl.database))  # -----------------------------------------------------------------------------------
    readNarrative()
    string = ''

    try:
        paths = [
                 ]
        i = 0

        # Play the game
        while True:  # leave_phone_booth, look_for_others, run_away_from_the_light, climb_out, run_away_from_the_light
            # Get the users narrative selection
            getNarrativeOptions()

            if glbl.do_auto_select is False:
                # print(pc.ICyan + '\nPlease select your narrative:\n' + pc.Reset + str(list(glbl.next_addresses)))
                print('\nPlease select your narrative:\n' + str(list(glbl.next_addresses)))
                if i < len(paths):
                    string = paths[i]
                else:
                    string = input()
                print("")
                i += 1

                with open("log_file.txt", "a") as log_file:
                    log_file.write('User Select - ' + str(string) + '\n')
            # Or automatically select the next element
            else:
                glbl.do_auto_select = False
                for address in glbl.next_addresses:
                    if 'auto' in glbl.next_addresses[address]:
                        string = 'auto'
                    else:
                        string = list(glbl.next_addresses)[0]
                with open("log_file.txt", "a") as log_file:
                    log_file.write('Auto Select - ' + str(string) + '\n')

            # Double check that the user hasn't made an error
            if updateAddresses(string, False) is False:
                # print('\n' + pc.IRed + 'ERROR - "' + str(string) + '" IS NOT AN OPTION!' + pc.Reset)
                # print(pc.IBlue + 'Please try again.' + pc.Reset)
                print('\nERROR - "' + str(string) + '" IS NOT AN OPTION!')
                print('Please try again.')
                with open("log_file.txt", "a") as log_file:
                    log_file.write('User Error - ERROR - "' + str(string) + '" IS NOT AN OPTION!' + '\n')
            else:
                readNarrative()
    except Exception as e:
        with open("log_file.txt", "a") as log_file:
            log_file.write('Program Error - {0}'.format(e) + '\n')
        print('{0}'.format(e))
    finally:
        print('ERROR HAS OCCURRED')
        input()


if __name__ == '__main__':
    main()
















