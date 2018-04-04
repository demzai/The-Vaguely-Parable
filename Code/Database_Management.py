"""
# Sets up the narrative database and manages its usage
"""

# Dependencies
import Extract_Narrative as en
import Print_Colour as pc
import Code_Interpreter as ci


def getAllDatabases(files, folders, folderID=""):
    """
    # Obtain all of the database files
    :param files:
    :param folders:
    :param folderID:
    :return:
    """
    database_files = []
    for file in files:
        if files[file][-4:] == '.csv':
            database_files = database_files + [[folderID, files[file]]]
    for folder in folders:
        currFolderID = folderID + folder + '/'
        directory = folders[folder]
        database_files = database_files + getAllDatabases(directory[1], directory[2], currFolderID)
    return database_files


def convertToGlobalAddress(address, global_appendage):
    """
    # Convert a local address into a global address
    :param address:
    :param global_appendage:
    :return:
    """
    directory_difference = global_appendage.count('/') - address.count('/')

    if (directory_difference <= 1) and (address[0] != '#'):
        # Add on any missing directories
        directory_levels = global_appendage.split('/')
        missing_addresses = ""
        for i in range(0, directory_difference):
            missing_addresses = missing_addresses + directory_levels[i] + '/'
        return missing_addresses + address
    else:
        return address


def listToMap(list_of_values):
    """
    # Convert a list into a map
    :param list_of_values:
    :return:
    """
    mapped_values = {}
    for entry in list_of_values:
        if entry[0] in mapped_values:
            # mapped_values[entry[0]] = mapped_values[entry[0]] + [[entry[1], entry[2]]]
            mapped_values[entry[0]].update({entry[2]: entry[1]})
        else:
            # mapped_values.update({entry[0]: [[entry[1], entry[2]]]})
            mapped_values.update({entry[0]: {entry[2]: entry[1]}})
    return mapped_values


def getStoryDatabase(files, folders):
    # Find database files
    """
    # Obtain & sort all .csv files into a single database
    :param files:
    :param folders:
    :return:
    """
    databases = getAllDatabases(files, folders)

    # Extract contents
    lines = []
    for database in databases:
        csv_lines = en.splitCSV(en.getFileContents(database[1]))

        # Format addresses appropriately
        for entry in csv_lines:
            entry[0] = convertToGlobalAddress(entry[0], database[0])
            entry[1] = convertToGlobalAddress(entry[1], database[0])
        lines = lines + csv_lines

    # Convert the list into a map and return (improves code readability and access time)
    return listToMap(lines)


def getFromMap(key, map_of_values):
    """
    # Perform a secure "get" from the map
    :param key:
    :param map_of_values:
    :return:
    """
    if str(key) in map_of_values:
        return map_of_values[key]
    else:
        pc.printC("ERROR: INVALID ID DETECTED - " + str(key), "FAIL")
        return None


def parseDatabaseEntry(entry):
    """
    Given an input from a database, resolve it based on its type and return
    :param entry:
    :return:
    """
    # Treat as any other text; clean it and deduce what type of input it is
    assessed = en.cleanFileContents(entry[0])[0]
    # If text-only, then assume it is an address and return it
    if assessed[0] == 'Text':
        return {entry[1]: entry[0]}

    # If code-only, then interpret it and return the result as a string
    elif assessed[0] == 'Variable' or assessed[0] == 'Code':
        code_results = ci.interpretCode(assessed[1])
        if isinstance(code_results, list):
            return_map = {}
            for result in code_results:
                return_map.update({result[1]: result[0]})
            return return_map
        else:
            return {entry[1]: str(code_results)}

    # If text containing code, then parse it to get the correct result
    elif assessed[0] == 'Container':
        return {entry[1]: ci.parseContainerCode(assessed[1], assessed[2])}

    # Otherwise the author has asked for something invalid
    else:
        raise ValueError("ERROR - " + str(assessed) + " IS NOT A VALID ENTRY!")


# # Uncomment for testing
if __name__ == '__main__':
    import Find_Files as ff
    from Globals import start_directory
    directories = ff.discoverFiles(start_directory)
    db = getStoryDatabase(directories[0], directories[1])
    # for j in db:
    #     pc.printC(str(db[j]), "WARNING")

    # Test the database entry parser
    print(parseDatabaseEntry(['0/0b', 'auto']))
