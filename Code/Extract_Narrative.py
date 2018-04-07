"""
# Reads a given file, determines their nature and, where relevant, extracts the codes prevalent in each line
"""

import re
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
            elif codeSegment is True:
                isCode = isCode + ["Segment"]
            elif sentence[1] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" and sentence[-1] != ')':
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
    for i in range(0, len(lines)):
        # Remove comments and excess whitespace...
        # If a code
        # print(pc.IYellow + str(isCode[i]) + ' - ' + str(lines[i]) + pc.Reset)  # -----------------------------------
        if isCode[i] == 'Code' or isCode[i] == 'Variable' or \
                (isCode == 'Segment' and len(lines[i]) >= 2 and lines[i][:2] == '//'):
            lines[i] = re.sub("\s*//.*", "", lines[i])
            lines[i] = re.sub("\s", "", lines[i])
        # If a segment then take extra care around textual data
        elif len(lines[i]) is not 0 and isCode[i] == 'Segment':
            # Remove comments
            lines[i] = re.sub("\s*//.*", "", lines[i])
            # Split into csv units
            sections = lines[i].split(',')
            lines[i] = ''
            combo = ''
            # For each csv unit
            for j in range(0, len(sections)):
                section = sections[j].strip()  # Remove whitespace at the beginning and end

                # If start of a string detected with no end, then stack the string together...
                if combo == '' and len(section) > 1 and section[0] == '"' and section[-1] != '"' or \
                        combo != '' and len(section) is not 0 and section[-1] != '"':
                    combo += sections[j] + ','
                    continue
                # ... until the end piece is detected
                elif combo != '' and len(section) is not 0 and section[-1] == '"':
                    section = (combo + sections[j]).strip()
                    combo = ''

                # If a string, then add without further modification
                if len(section) > 1 and section[0] == '"' and section[-1] == '"' and section != '"':
                    lines[i] += section + ','
                    continue
                section = re.sub("\s*//.*", "", section)
                lines[i] += re.sub("\s", "", section) + ','
            lines[i] = lines[i][:-1]

        elif len(lines[i]) is not 0 and lines[i][0] == '_':
            lines[i] = lines[i][1:]

        # Ignore empty lines
        if lines[i].strip() is not "":
            sentence = sentence + [[isCode[i], lines[i]]]
        # print(pc.IGreen + str(isCode[i]) + ' - ' + str(lines[i]) + pc.Reset)  # ------------------------------------
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
