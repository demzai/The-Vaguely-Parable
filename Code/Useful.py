# Delay time example
import time
print("before")
time.sleep(1.5)
print("after")


# Example console interactions
print("Please type something:")
string = "ignore"
# string = input()
print("You typed:", string)


# Write to a file example
fileObject = open("test.txt", 'w')
fileObject.write("Testing 1 2 3, can you hear me?\nNope\nHa, ha, ha. Very funny\nWhat was that?")
fileObject.close()


# Read from a file example
fileObject = open("test.txt", 'r')
fileContents = fileObject.read()
print(fileContents)
fileObject.close()


# Type conversion example
print(str(int("7"*7)/7))  # Always works
try:
    var = int("bob")
except ValueError:
    print("Bob is not a number")


# Printing to console in different colours:
class Colours:
    HEADER = '\033[95m'
    OK_BLUE = '\033[94m'
    OK_GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END_TEXT = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


print(Colours.WARNING + "Insert Coloured Text Here!!!" + Colours.END_TEXT)


# Valid file & folder detection
# [^\/\\\:\*\?\"\<\>\|\W]+\)[^\/\\\:\*\?\"\<\>\|\W]*\.(txt|csv)
import os, glob
folders = glob.glob('*)*' + os.path.sep)
files = glob.glob("*)*.*")


# Regular Expression Example:
import re
string = "\t hello _ world\t!"
regex = "[\s]+"
result = re.sub(regex, "", string, flags=re.MULTILINE)
removed = re.findall(regex, string, flags=re.MULTILINE)
print(regex + "\n" + string + "\n" + result)
print(removed)


# Regular Expressions
# https://regex101.com/
# Comments inc prior whitespace:
#   \s*\/\/[\S\t ]*
# Insert into Map code:
#   \n#[A-Z][a-zA-Z_]*,[ \t]*[^\s\\\:\*\?\"\<\>\|\n\r\0]*\n
# Extract from Map code:
#   \n#[A-Z][a-zA-Z_]*,?[ \t]*
# Code block start & end detection (\n###\n)
#   \n#{3}\n[\s\S]{0,}?\n#{3}\n?
# White-space detection (for removal)
#   [\s]+


# Map / Dictionary Example:
map_ = {"key": 'value', "num": 5318008, "bin": True}
map_.update({"life": "death"})
print(str(map_["key"]) + ", " + str(map_["num"]) + ", " + str(map_["bin"]) + ", " + str(map_["life"]))












