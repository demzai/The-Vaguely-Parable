import os
import glob
import re


# Valid file & folder detection
# [^\/\\\:\*\?\"\<\>\|\W\#]+\)[^\/\\\:\*\?\"\<\>\|\W\#]*\.(txt|csv)
# result = glob.glob("../**/*)*" + os.path.sep, recursive=True)


# Standardised, yet generic, search function
def search(directory="", foldersOnly=False, searchTerm='*)*', recurse=False):
    searchEnd = ""
    if foldersOnly is True:
        searchEnd = os.path.sep
    discoveredItems = glob.glob(directory + searchTerm + searchEnd, recursive=recurse)
    return discoveredItems


# Specialised search for files only
def findFiles(directory="", type=".*"):
    return search(directory, False, '*)*'+type, False)


# Specialised search for folders only
def findFolders(directory=""):
    return search(directory, True, '*)*', False)


# Remove folder extensions attached to file names
def removeExcessDirectories(objectName="", isFile=True, codeDeterminer="\\"):
    if isFile is True:
        return objectName.split(codeDeterminer)[-1]
    else:
        return objectName.split(codeDeterminer)[-2]


# Obtain a code and determine its validity
def getCode(objectName=")", isFile=True, codeDeterminer=")"):
    # @todo reducedObjectName here only because it may simplify issues later
    reducedObjectName = removeExcessDirectories(objectName, isFile)
    code = reducedObjectName.split(codeDeterminer)[0]

    # Determine the validity of the code
    numErrors = re.findall('.*\W+.*', code, flags=re.MULTILINE).__len__()
    if numErrors is 0:
        return code
    else:
        return False


# Main function for finding and returning files and folders
def discoverFiles(directory=""):
    # Find possibly relevant files and folders
    filesList = findFiles(directory)
    foldersList = findFolders(directory)

    # Generate a mapping between file codes and the files themselves
    files = {}
    for fileName in filesList:
        code = getCode(fileName, True)
        if code is not False:
            files.update({code: fileName})

    # Generate a mapping between folder codes and the folders themselves
    folders = {}
    for folderName in foldersList:
        code = getCode(folderName, False)
        if code is not False:
            [subFiles, subFolders] = discoverFiles(folderName)
            folders.update({code: [folderName, subFiles, subFolders]})

    # Return the mapping
    return [files, folders]


# Uncomment for testing purposes
# [fils, folds] = discoverFiles("../Story Segments/")
# var = fils
# for a in var:
#     print(a + ",\t" + str(var[a]))














