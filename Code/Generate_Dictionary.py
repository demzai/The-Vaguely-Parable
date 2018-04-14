"""
Generates dictionary files
"""

# Dependencies
# import lxml.html as lh
import requests as req
import re
import num2words as nw
import os
import pocketsphinx as ps


# Global Values
grammar_directory = "Grammars/"
dictionary_directory = "Dictionaries/"
confidence_threshold = 1*10**-5
inflexions = {
    "huh": ["huh"],
    "like": ["like"],
    "um": ["um"],
    "umm": ["umm"],
    "er": ["er"],
    "err": ["err"],
    "hm": ["hm"],
    "hmm": ["hmm"],
    "uh": ["uh"],
    "uhh": ["uhh"],
    "eh": ["eh"],
    "ehh": ["ehh"],
    "ah": ["ah"],
    "ahh": ["ahh"],
    "ooh": ["ooh"],
    "oh": ["oh"],
    "please": ["please"],
    "thanks": ["thanks"],
    "thank you": ["thank you"],
    "ta": ["ta"],
    "could you": ["could you"],
    "vaguely": ["vaguely"],
    "I'd like to": ["I'd like to"],
    "could I": ["could I"],
    "can I": ["can I"]
}


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


# noinspection SpellCheckingInspection
def getDictionary(dictionary_path=ps.get_model_path()+'\\cmudict-en-us.dict', dictionary=None):
    """
    Reads a given dictionary file and generates a map of words to their phonemes
    :param dictionary_path:
    :param dictionary
    :return:
    """
    dictionary_contents = readFile(dictionary_path)
    word_list = re.findall('(^|\n)([-a-zA-Z\.\'\(\)0-9]+) (.*)', dictionary_contents)
    for i in range(len(word_list)):
        word_list[i] = word_list[i][1:]

    if dictionary is None:
        dictionary = dict(word_list)
    else:
        dictionary.update(dict(word_list))
    print(len(dictionary))
    return dictionary


def getSentences(file_locale):
    """
    Extracts a list of sentences to process, and splits them off into groups
    :param file_locale:
    :return:
    """
    # Get each individual sentence in each sentence set
    sentence_sets = []
    for text in readFile(file_locale).split('\n\n'):
        text = text.strip()
        sentence_sets += [text.split('\n')]
    return sentence_sets


def getUniqueWords(sentence_sets):
    """
    Given a set of sentences, generate a list of unique words used within them
    :param sentence_sets:
    :return:
    """
    unique_words = {}
    # For each set of sentences
    for sentences in sentence_sets:
        words = {}
        # For each sentence within that set
        for j in range(1, len(sentences)):
            sentence = sentences[j]
            words.update({sentence.replace(' ', '_'): []})
            # For each word within the sentence
            for word in sentence.replace('-', ' ').replace('_', ' ').split(' '):
                # Add to a map to remove duplicates
                words.update({word: []})
        # Store the result
        unique_words.update({sentences[0]: list(words.keys())})
    return unique_words


def formatWordsList(words):
    """
    # Takes in a list of words and formats them nicely for the grammar interpreter
    :param words:
    :return:
    """
    return_list = []
    for word in words:
        word = word.replace('%27', "'")
        # If '%' is contained, then the word is probably not a word!
        if '%' not in word:
            # Convert numbers to words
            numbers = re.findall('[0-9]+', word)
            for num in numbers:
                word.replace(num, nw.num2words(num), 1)
            # Remove underscores, dashes and apostrophes
            # word = str(word).replace('_', ' ').replace('-', ' ')
            return_list += [word]
    return return_list


def getSynonyms(word, word_set):
    """
    For a given word, searches for synonyms on both thesaurus.com and powerthesaurus.org
    :param word:
    :return:
    """
    # Add the current word to the synonyms list
    word_set.update({formatWordsList([word])[0]: 0})

    # Get "narrower" words from http://powerthesaurus.org
    try:
        site = req.get('http://powerthesaurus.org/' + word + '/narrower').text
        discovered = re.findall('class="pt-thesaurus-card__term-title"><a href="/(.*)/narrower"', site)
        for i in formatWordsList(discovered):
            for k in i.split(' '):
                word_set.update({k: 0})
    except OSError as e:
        print('Failed to load site 2 HTTP resource, {0}'.format(e))

    # Get synonyms from http://powerthesaurus.org
    if len(word_set) is 0:
        try:
            site = req.get('http://powerthesaurus.org/' + word + '/synonyms').text
            discovered = re.findall('class="pt-thesaurus-card__term-title"><a href="/(.*)/synonyms"', site)
            for i in formatWordsList(discovered):
                for k in i.split(' '):
                    word_set.update({k: 0})
        except OSError as e:
            print('Failed to load site 2 HTTP resource, {0}'.format(e))

    # Get related words from http://powerthesaurus.org
    try:
        site = req.get('http://powerthesaurus.org/' + word + '/related').text
        discovered = re.findall('class="pt-thesaurus-card__term-title"><a href="/(.*)/related"', site)
        for i in formatWordsList(discovered):
            for k in i.split(' '):
                word_set.update({k: 0})
    except OSError as e:
        print('Failed to load site 2 HTTP resource, {0}'.format(e))

    return word_set


def genSubDictionary(words_list, full_dictionary, file_location):
    # Generate a full words list
    words = inflexions
    for word in words_list:
        if __name__ == '__main__':
            print('\t' + word)
        words = getSynonyms(word, words)
    words = sorted(list(words.keys()))
    if __name__ == '__main__':
        print('\t\t' + str(words))

    # Generate a new dictionary based on the the words list and full dictionary
    with open(file_location, 'w') as dictionary_file:
        for phrase in words:
            phrase = phrase.replace('_', ' ').replace('-', ' ')
            for word in phrase.split(' '):
                if word in full_dictionary:
                    i = 2
                    # Add the word
                    dictionary_file.write(word + ' ' + full_dictionary[word] + '\n')
                    # Add other phonetic variations, if they exist
                    while word + '({0})'.format(i) in full_dictionary:
                        dictionary_file.write(word + '({0})'.format(i) + ' ' + full_dictionary[word] + '\n')
                        i += 1
                else:
                    print("\t\tWARNING: {0} was ignored as it was not found within the master dictionary!".format(word))


# noinspection PyBroadException
def genDictionaryForSelectionSet(selections, dictionary_name):
    """
    Given a list of narrative selections, find their corresponding grammars and generate
        a meta-grammar to search for all of them
    :param selections:
    :param dictionary_name:
    :return:
    """
    # Find valid selections
    group_dictionary = {}
    for selection in selections:
        shorthand = str(selection).replace('_', '')
        file = dictionary_directory + shorthand + '.dict'
        try:
            if os.path.isfile(file) is True:
                current_dictionary = getDictionary(file)
                group_dictionary.update(current_dictionary)
        except Exception:
            continue

    # Create a dictionary file using the valid selections
    dictionary_file_location = dictionary_directory + str(dictionary_name) + '.dict'

    word_list = sorted(list(group_dictionary.keys()))
    with open(dictionary_file_location, 'w') as dictionary_file:
        for word in word_list:
            dictionary_file.write(word + ' ' + group_dictionary[word] + '\n')

    # Return the file directory and name
    return dictionary_file_location


def main():
    full_dictionary = getDictionary()
    sentence_set = getSentences(grammar_directory + "Selection Texts.txt")
    unique_words = getUniqueWords(sentence_set)

    for sub_list in unique_words:
        if __name__ == '__main__':
            print(sub_list + ':')
        genSubDictionary(unique_words[sub_list], full_dictionary,
                         str(dictionary_directory) + str(sub_list).replace(' ', '') + '.dict')


if __name__ == '__main__':
    main()


