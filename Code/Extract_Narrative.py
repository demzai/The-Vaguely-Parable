"""
# Reads a given file, determines their nature and, where relevant, extracts the codes prevalent in each line
"""

import re
if __name__ == '__main__':
    import Print_Colour as pc


def getDynamicText(sentence):
    """
    # Determine text entries to be replaced
    :param sentence:
    :return:
    """
    codes = re.findall("(^|\\\{2,}|[^\\\])(#\S+)", sentence)
    return codes


def findCodeLines(sentences):
    """
    # Determine which sentences are code
    :param sentences:
    :return:
    """
    isCode = []
    codeSegment = False
    for sentence in sentences:
        if sentence.__len__() is 0:
            isCode = isCode + ["Text"]
        elif sentence[0] is '#' or sentence[:2] == '//':
            if (sentence.__len__() >= 3) and (sentence[:3] == '###'):
                codeSegment = not codeSegment
                isCode = isCode + ["Code"]
            elif sentence[1] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                isCode = isCode + ["Variable"]
            else:
                isCode = isCode + ["Code"]
        else:
            if codeSegment is True:
                isCode = isCode + ["Segment"]
            elif getDynamicText(sentence).__len__() is not 0:
                isCode = isCode + ["Container"]
            else:
                isCode = isCode + ["Text"]
    return isCode


def cleanFileContents(text):
    """
    # Split lines and remove empty lines
    :param text:
    :return:
    """
    # Determine which lines are code to determine which comments can be scrubbed
    lines = [i.strip() for i in text.split("\n")]
    isCode = findCodeLines(lines)
    sentence = []
    for i in range(0, lines.__len__()):
        # Remove comments and excess whitespace
        if isCode[i] != 'Container' and isCode[i] != 'Text':
            lines[i] = re.sub("\s*//.*", "", lines[i])
            lines[i] = re.sub("\s", "", lines[i])
        elif lines[i].__len__() is not 0 and lines[i][0] == '_':
            lines[i] = lines[i][1:]

        # Ignore empty lines
        if lines[i].strip() is not "":
            sentence = sentence + [[isCode[i], lines[i]]]
    return sentence


def getFileContents(fileLocale):
    """
    # Open the given file and extract its contents
    :param fileLocale:
    :return:
    """
    fileObject = open(fileLocale, 'r')
    fileContents = fileObject.read()
    fileObject.close()
    text = cleanFileContents(fileContents)

    # Extract codes for easier processing later on
    for line in range(0, text.__len__()):
        # Texts have no codes
        if text[line][0] == 'Text':
            text[line] = text[line] + [[]]
        # Containers are texts with codes. Therefore, extract and add them
        elif text[line][0] == 'Container':
            codes = [i[1] for i in getDynamicText(text[line][1])]
            text[line] = text[line] + [codes]
        # Segments are codes without the #segement(---) identifier
        elif text[line][0] == 'Segment':
            text[line] = text[line] + [['#segment(' + str(text[line][1]) + ')']]
        else:
            text[line] = text[line] + [[text[line][1]]]
    return text


def splitCSV(lines):
    """
    # Separate database entries
    :param lines:
    :return:
    """
    result = []
    for line in lines[1:-1]:
        line[1] = "".join(line[1].split())
        result = result + [line[1].split(",")]
    return result


if __name__ == '__main__':
    # file = "test.txt"
    # file_lines = getFileContents(file)
    # # Print file lines
    # for s in range(0, file_lines.__len__()):
    #     print(pc.IPurple + str(file_lines[s][0]) + ',\t' + \
    #           pc.IYellow + str(file_lines[s][1]) + ',\t' +  \
    #           pc.IGreen + str(file_lines[s][2]) + pc.Reset)

    file = "a) Pass/DB) Database Test.csv"
    csv_lines = splitCSV(getFileContents(file))
    # Print CSV lines
    for s in range(0, csv_lines.__len__()):
        print(pc.IPurple + str(csv_lines[s][0]) + ',\t' + \
              pc.IYellow + str(csv_lines[s][1]) + ',\t' +  \
              pc.IGreen + str(csv_lines[s][2]) + pc.Reset)
