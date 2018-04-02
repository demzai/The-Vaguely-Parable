"""
Finds files, creating a database of their locations
Provides a file location if given a valid code
"""


# Dependencies
import os
import glob
import re
from Globals import start_directory


def search(directory="", foldersOnly=False, searchTerm='*)*', recurse=False):
    """
    # Standardised, yet generic, search function
    :param directory:
    :param foldersOnly:
    :param searchTerm:
    :param recurse:
    :return:
    """
    searchEnd = ""
    if foldersOnly is True:
        searchEnd = os.path.sep
    discoveredItems = glob.glob(directory + searchTerm + searchEnd, recursive=recurse)
    return discoveredItems


def findFiles(directory="", file_type=".*"):
    """
    # Specialised search for files only
    :param directory:
    :param file_type:
    :return:
    """
    return search(directory, False, '*)*' + file_type, False)


def findFolders(directory=""):
    """
    # Specialised search for folders only
    :param directory:
    :return:
    """
    return search(directory, True, '*)*', False)


def removeExcessDirectories(objectName="", isFile=True, codeDeterminer="\\"):
    """
    # Remove folder extensions attached to file names
    :param objectName:
    :param isFile:
    :param codeDeterminer:
    :return:
    """
    if isFile is True:
        return objectName.split(codeDeterminer)[-1]
    else:
        return objectName.split(codeDeterminer)[-2]


def getCode(objectName=")", isFile=True, codeDeterminer=")"):
    """
    # Obtain a code and determine its validity
    :param objectName:
    :param isFile:
    :param codeDeterminer:
    :return:
    """
    reducedObjectName = removeExcessDirectories(objectName, isFile)
    code = reducedObjectName.split(codeDeterminer)[0]

    # Determine the validity of the code
    numErrors = re.findall('.*\W+.*', code, flags=re.MULTILINE).__len__()
    if numErrors is 0:
        return code
    else:
        return False


def discoverFiles(directory=""):
    # Find possibly relevant files and folders
    """
    # Main function for finding and returning files and folders
    :param directory:
    :return:
    """
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


def getFileFromCode(code, file_locales, code_determiner='/'):
    """
    # Given a file code, provide the file location if it exists
    :param code:
    :param file_locales:
    :param code_determiner:
    :return:
    """
    code = code.split(code_determiner)
    file_locales = [start_directory] + file_locales
    code_id = 0
    try:
        for i in range(0, code.__len__()-1):
            code_id = i
            file_locales = file_locales[2][code[i]]
        code_id = code.__len__()-1
        file = file_locales[1][code[-1]]
    except KeyError:
        print('BAD INDEX AFTER "' + str(file_locales[0]) + '" - "' + str(code[code_id]) + '"')
        return ""
    finally:
        del code, file_locales, code_determiner, code_id
    return file


if __name__ == '__main__':
    directories = discoverFiles(start_directory)
    var = directories[0]
    for a in var:
        print(a + ",\t" + str(var[a]))
    while True:
        print("Please enter a code:")
        string = input()
        print(getFileFromCode(string, [directories[0], directories[1]]))



