# Dependencies
import Extract_Narrative as en
import Print_Colour as pc


# Obtain all of the database files
def getAllDatabases(files, folders, folderID=""):
    database_files = []
    for file in files:
        if files[file][-4:] == '.csv':
            database_files = database_files + [[folderID, files[file]]]
    for folder in folders:
        currFolderID = folderID + folder + '/'
        directory = folders[folder]
        database_files = database_files + getAllDatabases(directory[1], directory[2], currFolderID)
    return database_files


# Convert a local address into a global address
def convertToGlobalAddress(address, global_appendage):
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


# Convert a list into a map
def listToMap(list_of_values):
    mapped_values = {}
    for entry in list_of_values:
        if entry[0] in mapped_values:
            mapped_values[entry[0]] = mapped_values[entry[0]] + [[entry[1], entry[2]]]
            # map[entry[0]].update({entry[2]: entry[1]})
        else:
            mapped_values.update({entry[0]: [[entry[1], entry[2]]]})
            # map.update({entry[0]: {entry[2]: entry[1]}})
    return mapped_values


# Obtain & sort all .csv files into a single database
def getStoryDatabase(files, folders):
    # Find database files
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


# Perform a secure "get" from the map
def getFromMap(key, map_of_values):
    if str(key) in map_of_values:
        return map_of_values[key]
    else:
        pc.printC("ERROR: INVALID ID DETECTED - " + str(key), "FAIL")
        return None


# # Uncomment for testing
# import Find_Files as ff
# story_directory = "../Story Segments/"
# [files, folders] = ff.discoverFiles(story_directory)
# db = getStoryDatabase(files, folders)
# for i in db:
#     pc.printC(str(db[i]), "WARNING")
