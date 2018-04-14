# """
# # This is the testing ground.
# # Develop functions here, but do not leave them here!
# # This is a glorified playground to make a mess in!
# """
#
# import re
# import os
#
# grammar_directory = "Grammars/"
# # noinspection SpellCheckingInspection
# files = []
# words_list = "words_sorted.gram"
#
#
# def readFile(file_location):
#     """
#     Generic, simplified, function to extract the contents of a file
#     :param file_location:
#     :return:
#     """
#     fileObject = open(file_location, 'r')
#     fileContents = fileObject.read()
#     fileObject.close()
#     return fileContents
#
#
# def main():
#     word_map = {}
#     dictionary = readFile(grammar_directory + words_list)
#     entries = re.findall('.*\n', dictionary)
#     print(len(entries))
#     print(entries[0])
#     for entry in entries:
#         name = re.findall('<.*>', entry)[0]
#         word_map.update({name: entry})
#
#     for file in files:
#         print(grammar_directory + file)
#         contents = readFile(grammar_directory + file)
#
#         # Comment out the import
#         re.sub('import <words\.\*>;', '// import <words.*>;', contents)
#         with open(grammar_directory + file, 'w') as grammar:
#             grammar.write(contents)
#
#         # Get list of words to add
#         file_words = re.findall('<\w+>', contents)[1:]
#         file_words_map = {}
#
#         # Get list of unique words
#         for word in file_words:
#             file_words_map.update({word: ''})
#         file_words = list(file_words_map.keys())
#
#         # Add the words
#         with open(grammar_directory + file, 'a') as grammar:
#             grammar.write('\n')
#             for word in file_words:
#                 grammar.write(word_map[word])
#
#
# if __name__ == '__main__':
#     main()


