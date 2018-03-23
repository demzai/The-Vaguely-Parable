# Example console interactions
print("Please type something:")
string = input()
print("You typed:", string)


# Write to a file example
fileObject = open("test.txt", 'w')
fileObject.write("Testing 1 2 3, can you hear me?")
fileObject.close()


# Read from a file example
fileObject = open("test.txt", 'r')
fileContents = fileObject.read()
print(fileContents)
fileObject.close()



