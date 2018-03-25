# Printing to console in different colours:
colours = {
    "HEADER": '\033[95m',
    "OK_BLUE": '\033[94m',
    "OK_GREEN": '\033[92m',
    "WARNING": '\033[93m',
    "FAIL": '\033[91m',
    "END_TEXT": '\033[0m',
    "UNDERLINE": '\033[4m'}


def printC(text, console="STANDARD"):
    if (console in colours) and (console != "END_TEXT"):
        print(colours[console] + text + colours["END_TEXT"])
    else:
        print(text)



