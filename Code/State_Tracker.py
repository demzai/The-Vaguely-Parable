"""
The functions defined within aid with the tracking and maintenance of the system state machine
"""

# Dependencies:
import Database_Management as dm
import Extract_Narrative as en
import Find_Files as ff
import Globals as glbl
import Reader


def getStartNode(files):
    """
    # Read the initialisation file
    :param files:
    :return:
    """
    initial_file = files['Init']
    return (en.getFileContents(initial_file))[0][1]


def parseMapOfAddresses(map_of_values):
    """
    Parse each address through the interpreter
    :param map_of_values:
    :return:
    """

    # Create stacks to hold direct and referenced addresses
    direct_addresses = []
    reference_addresses = []

    for address in map_of_values:
        new_address = dm.parseDatabaseEntry([map_of_values[address], address])

        # Referenced addresses have a lower priority than current addresses, so delay their assimilation
        if len(map_of_values[address]) > 1 and map_of_values[address][:2] == '#&':
            reference_addresses += [new_address]
        # Update the address list, with a preference for pre-existing addresses
        else:
            direct_addresses += [new_address]
    return [direct_addresses, reference_addresses]


def addListToMap(address_map, list_to_add):
    """
    Iteratively add addresses from the list to the address map
    :param address_map:
    :param list_to_add:
    :return:
    """
    for address in list_to_add:
        address.update(address_map)
        address_map = address
    return address_map


def parseInputAndAddToMap(input_values, is_list, map_of_values):
    """
    Parses an input list or map through the interpreter and adds the results to the final map
    :param input_values:
    :param is_list:
    :param map_of_values:
    :return:
    """
    # Convert to a map if necessary
    if is_list is True:
        options = addListToMap({}, input_values)
    else:
        options = input_values

    # Parse through the interpreter & add to the map
        # Direct first in case references overwrite desired addresses
    [direct, referenced] = parseMapOfAddresses(options)
    map_of_values = addListToMap(map_of_values, direct)
    map_of_values = addListToMap(map_of_values, referenced)
    return map_of_values


def pairWithName(set_of_values, name):
    """
    Creates a map of values with the same name value paired with them
    :param set_of_values:
    :param name:
    :return:
    """
    pair = {}
    for value in set_of_values:
        pair.update({value: name})
    return pair


def getNarrativeOptions():
    """
    Creates a list of the next addresses accessible to the user
    :return:
    """
    # Reset the next_addresses stack
    glbl.next_addresses = {}

    # Get the list of options available
    if glbl.is_reading is True:
        # Get list of addresses for interrupting the narrator
        options = addListToMap({}, glbl.interrupt_addresses)
    else:
        # Get list of addresses to progress the narrative
        options = dm.getFromMap(glbl.address_stack[-1], glbl.database)

    # Add the narratives to the list
    glbl.next_addresses = parseInputAndAddToMap(options, False, glbl.next_addresses)
    if glbl.is_reading is True:
        address_types = pairWithName(set(glbl.next_addresses), 'interrupt')
    else:
        address_types = pairWithName(set(glbl.next_addresses), 'narrative')

    # Insert addresses which are constant throughout the entire narrative
    if glbl.is_reading is False:
        # Constant addresses, e.g. "repeat" or "date and time"
        prev = set(glbl.next_addresses)
        glbl.next_addresses = parseInputAndAddToMap(glbl.constant_addresses, True, glbl.next_addresses)
        address_types.update(pairWithName(set(glbl.next_addresses)-prev, 'constant'))

        # Error addresses, e.g. "taking too long", "illegible", or "creator messed up"
        prev = set(glbl.next_addresses)
        glbl.next_addresses = parseInputAndAddToMap(glbl.error_addresses, True, glbl.next_addresses)
        address_types.update(pairWithName(set(glbl.next_addresses)-prev, 'user_error'))

    # Remove certain addresses if they exist
    for address in glbl.ignore_addresses:
        if isinstance(address, str) or isinstance(address, int) or isinstance(address, float):
            glbl.next_addresses.pop(address, None)
            address_types.pop(address, None)
    glbl.ignore_addresses = []

    # Return the paired names
    return address_types


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
    :type reader: Reader.ReaderObj
    :param reader:
    :return:
    """
    narrative_file = ff.getFileFromCode(glbl.address_stack[-1], glbl.file_locales)
    narrative_text = en.getFileContents(narrative_file)
    reader.stack += narrative_text


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


