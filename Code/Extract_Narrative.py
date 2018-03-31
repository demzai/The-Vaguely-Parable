import re


# Remove comments and empty lines
def cleanFileContents(text):
    sentence = []
    for line in text.split("\n"):
        # Remove comments and excess whitespace at the start and end of the line
        line = re.sub("\s*//.*", "", line)
        line = line.strip()

        # Ignore empty lines
        if line.strip() is not "":
            sentence = sentence + [line]
    return sentence


# Open the given file and extract its contents
def getFileContents(fileLocale):
    fileObject = open(fileLocale, 'r')
    fileContents = fileObject.read()
    fileObject.close()
    text = cleanFileContents(fileContents)
    return text


# Determine text entries to be replaced
def getDynamicText(sentence):
    codes = re.findall("#[\w&]*", sentence)
    return codes


# Determine which sentences are code
def findCodeLines(sentences):
    isCode = []
    codeSegment = False
    for sentence in sentences:
        if sentence[0] is '#':
            if (sentence.__len__() >= 3) and (sentence[:2] == '###'):
                codeSegment = not codeSegment
                isCode = isCode + ["True"]
            elif sentence[1] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                isCode = isCode + ["Variable"]
            else:
                isCode = isCode + ["True"]
        else:
            if codeSegment is True:
                isCode = isCode + ["True"]
            elif re.findall('(^|\\\{2,}|[^\\\])\#\S+', sentence).__len__() is not 0:
                isCode = isCode + ["Container"]
            else:
                isCode = isCode + ["False"]
    return isCode


# Separate database entries
def splitCSV(lines):
    result = []
    for line in lines:
        line = "".join(line.split())
        result = result + [line.split(",")]
    return result

# Uncomment for testing
# import Print_Colour as pr
# file = "a) Pass/DB) Database Test.csv"
# sentences = getFileContents(file)
# codeLines = findCodeLines(sentences)
# # sentences = splitCSV(sentences)
# for s in range(0, sentences.__len__()):
    # pr.printC(str(codeLines[s]) + '\t' + str(sentences[s]), "OK_BLUE")
    # dynamicText = getDynamicText(sentences[s])
    # if dynamicText.__len__() is not 0:
        # pr.printC(str(dynamicText), "OK_GREEN")

