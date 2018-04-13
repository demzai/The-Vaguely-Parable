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


import speech_recognition as sr
import pocketsphinx as ps
import os
import re


def readFile(file_location):
    """
    Generic, simplified, function to extract the contents of a file
    :param file_location:
    :return:
    """
    fileObject = open(file_location, 'r')
    fileContents = fileObject.read()
    fileObject.close()
    return fileContents


def getWordList(dictionary_path=ps.get_model_path()+'\\cmudict-en-us.dict'):
    dictionary = readFile(dictionary_path)
    word_list = re.findall('^|\n([-a-zA-Z\.\'\(\)0-9]+) (.*)', dictionary)
    return dict(word_list)


# Get synonyms list for each word
# Get list of unique words per sentence set
# For each unique word:
#   For each synonym:
#     If in dictionary, append new dictionary with that word and phoneme
# Do this for each narrative option with a grammar file / dictionary(?) and append to search-dictionary
# Sort the words into alphabetical order?



def recognise_sphinx(audio, dictionary):
    # Ensure inputs are correct
    assert isinstance(audio, sr.AudioData), "``audio_data`` must be audio data"
    if not os.path.isfile(dictionary):
        raise sr.RequestError("Missing PocketSphinx phoneme dictionary file: \"{}\"".format(dictionary))

    # Create decoder object
    config = ps.Decoder.default_config()
    config.set_string("-dict", dictionary)
    decoder = ps.Decoder()

    # Obtain audio data
    # The included language models require audio to be 16-bit mono 16 kHz in little-endian format
    raw_data = audio.get_raw_data(convert_rate=16000, convert_width=2)

    # Obtain recognition results
    decoder.start_utt()  # Begin utterance processing
    # Process audio data with recognition enabled (no_search = False), as a full utterance (full_utt = True)
    decoder.process_raw(raw_data, False, True)
    decoder.end_utt()  # Stop utterance processing

    return decoder


def main():
    getWordList()


if __name__ == '__main__':
    main()
