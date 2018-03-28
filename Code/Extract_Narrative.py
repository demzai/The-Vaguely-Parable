import re


# Remove comments and empty lines
def cleanFileContents(text):
    sentence = []
    for line in text.split("\n"):
        # Remove comments and excess whitespace at the start and end of the line
        line = re.sub("\s*\/\/.*", "", line)
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
    codes = re.findall("\#[\w\&]*", sentence)
    return codes


# Determine which sentences are code
def findCodeLines(sentences):
    isCode = []
    codeSegment = False
    for s in sentences:
        if s[0] is '#':
            if (s.__len__() >= 3) and \
                    (s[1] is '#') and \
                    (s[2] is '#'):
                codeSegment = not codeSegment
            if (s[1] is ' ') or (s[1] is '\t'):
                isCode = isCode + ["Error"]
            else:
                isCode = isCode + [True]
        else:
            if codeSegment is True:
                isCode = isCode + [True]
            else:
                isCode = isCode + [False]
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
# file = "a) Pass/DB) Database Test.txt"
# sentences = getFileContents(file)
# codeLines = findCodeLines(sentences)
# # sentences = splitCSV(sentences)
# for s in range(0, sentences.__len__()):
#     pr.printC(str(codeLines[s]) + '\t' + str(sentences[s]), "OK_BLUE")
#     dynamicText = getDynamicText(sentences[s])
#     if dynamicText.__len__() is not 0:
#         pr.printC(str(dynamicText), "OK_GREEN")

