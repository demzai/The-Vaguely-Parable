"""
Finds files, creating a database of their locations
Provides a file location if given a valid code
"""


# Dependencies
import os
import glob
import re
from Constants import *


# Standardised, yet generic, search function
def search(directory="", foldersOnly=False, searchTerm='*)*', recurse=False):
    searchEnd = ""
    if foldersOnly is True:
        searchEnd = os.path.sep
    discoveredItems = glob.glob(directory + searchTerm + searchEnd, recursive=recurse)
    return discoveredItems


# Specialised search for files only
def findFiles(directory="", file_type=".*"):
    return search(directory, False, '*)*' + file_type, False)


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


# Given a file code, provide the file location if it exists
def getFileFromCode(code, file_locales, code_determiner='/'):
    code = code.split(code_determiner)
    file_locales = [start_directory] + file_locales
    try:
        for i in range(0, code.__len__()-1):
            file_locales = file_locales[2][code[i]]
        file = file_locales[1][code[-1]]
    except KeyError:
        print('BAD INDEX AFTER "' + str(file_locales[0]) + '" - "' + str(code[i]) + '"')
        return ""
    return file


if __name__ == '__main__':
    [files, folders] = discoverFiles(start_directory)
    var = folders
    for a in var:
        print(a + ",\t" + str(var[a]))
    while True:
        print("Please enter a code:")
        string = input()
        print(getFileFromCode(string, [files, folders]))



