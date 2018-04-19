"""
The code in this file is dedicated to taking textual data in and providing
    a metric for how closely that text matches a given story option
"""


# Dependencies:
import os
import re
import ast
import time
import requests as req
import num2words as nw
import pocketsphinx as ps


# Globals:
grammar_directory = "Grammars/"
dictionary_directory = "Dictionaries/"
confidence_threshold = 0.0
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
    "thank": ["thank"],
    "ta": ["ta"],
    "could": ["could"],
    "vaguely": ["vaguely"],
    "I'd": ["I'd"],
    "can": ["can"]
}


def readFile(file_location):
    """
    Generic, simplified, function to extract the contents of a file
    :param file_location:
    :return:
    """
    with open(file_location, 'r') as fileObject:
        fileContents = fileObject.read()
    return fileContents


def writeFile(file_location, file_contents):
    """
    Generic, simplified, function to write the contents of a file
    :param file_location:
    :param file_contents:
    :return:
    """
    with open(file_location, 'w') as fileObject:
        fileObject.write(file_contents)
    return


# noinspection SpellCheckingInspection,PyTypeChecker
def getDictionary(dictionary_path=ps.get_model_path()+'\\cmudict-en-us.dict', dictionary=None):
    """
    Reads a given dictionary file and generates a map of words to their phonemes
    :param dictionary_path:
    :param dictionary
    :return:
    """
    dictionary_contents = readFile(dictionary_path)
    word_list = re.findall('(^|\n)([-a-zA-Z.\'()0-9]+) (.*)', dictionary_contents)
    for i in range(len(word_list)):
        word_list[i] = word_list[i][1:]

    if dictionary is None:
        dictionary = dict(word_list)
    else:
        dictionary.update(dict(word_list))
    # print(len(dictionary))
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


def formatWordsList(words):
    """
    # Takes in a list of words and formats them nicely for the grammar interpreter
    :param words:
    :return:
    """
    return_list = []
    for word in words:
        # If '%' is contained, then the word is probably not a word!
        word = word.replace('%27', "'")
        if '%' not in word:
            # Convert numbers to words
            numbers = re.findall('[0-9]+', word)
            for num in numbers:
                word.replace(num, nw.num2words(num))
            # Remove underscores, dashes and apostrophes
            word = str(word).replace('_', ' ').replace('-', ' ').strip()
            return_list += [word]
    return return_list


def getSynonyms(word, search_type='synonyms'):
    """
    For a given word, searches for synonyms on both thesaurus.com and powerthesaurus.org
    :param word:
    :param search_type:
    :return:
    """
    # Set up a request for information from the internet
    print(str(word))
    word_set = {formatWordsList([word])[0]: 0}
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 ' +
                      '(KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
    url = 'http://powerthesaurus.org/' + word + '/' + search_type

    # Attempt to get words from http://powerthesaurus.org
    try:
        r = req.get(url, headers=headers, timeout=10)
        time.sleep(2)
        site = r.text

        # Extract the results from the web-page HTML source
        discovered = re.findall('class="pt-thesaurus-card__term-title"><a href="/(.*)/' + search_type + '"', site)
        for i in formatWordsList(discovered):
            # If the word has a '%' in it after formatting, then it probably isn't a word
            if '%' in i:
                continue

            # Add the word or phrase into the thesaurus
            word_set.update({i: 0})

    # If failed, then provide an error message
    except OSError as e:
        print('Failed to load site HTTP resource, {0}'.format(e))

    # Return a list of unique words and phrases associated with the provided word
    return list(word_set.keys())


def genPhraseRegularExpression(phrase, is_whole_only=False):
    """
    Given a textual phrase, generate a regular expression for it
    :param is_whole_only:
    :type phrase: str
    :param phrase:
    :return:
    """
    phrase = phrase.strip()
    if bool(phrase) is False:
        return ''

    regex = '((^| )'
    # If searching for the whole phrase only then don't split for each word
    if is_whole_only is True:
        regex += str(phrase.strip()) + ')'
    else:
        for word in phrase.strip().split(' '):
            regex += str(word) + '|(^| )'
        regex = regex[:-6] + ')'

    return regex


def genPhraseGrammarRule(phrase):
    """
    Given a textual phrase, generate a grammar rule for it
    :type phrase: str
    :param phrase:
    :return:
    """
    phrase = phrase.strip()
    if bool(phrase) is False:
        return ''

    rule = '<' + phrase.replace(' ', '') + '> = ( [<inflexions>] '
    for word in phrase.strip().split(' '):
        rule += str(word) + ' [<inflexions>] '
    rule += ')'

    return rule


def genSentenceGrammarRule(sentence_set):
    """
    Creates a grammar rule for a given list of sentences
    :type sentence_set: list
    :param sentence_set:
    :return:
    """
    if bool(sentence_set) is False:
        return ''

    rule = '<' + sentence_set[0].replace(' ', '') + '> = '
    # Make each word reference another grammar rule, and consider each sentence via an OR statement
    for sentence in sentence_set[1:]:
        rule += '( <{0}> ) | '.format(str(sentence).strip().replace(' ', '> <'))
    rule = rule[:-2]

    return rule


def filterWordsList(sentence_set, dictionary):
    """
    Ensures that only words or phrases present within the dictionary are allowed
    :type sentence_set: list
    :type dictionary: dict
    :param sentence_set:
    :param dictionary:
    :return:
    """
    words = {}
    phrases = {}

    for phrase in sentence_set:
        is_good = True

        # Add words to the dictionary
        for word in str(phrase).split(' '):
            if word in dictionary:
                phoneme = dictionary[word]
                words.update({word: phoneme})
            else:
                is_good = False

        # If all words were good, then add the word or phrase to the phrases list
        if is_good is True:
            regex = genPhraseRegularExpression(phrase)
            grammar = genPhraseGrammarRule(phrase)
            phrases.update({phrase: [regex, grammar]})

    return [words, phrases]


def mergeThesauri(list_of_thesauri):
    """
    Given a list of thesauri, merge them into a single thesaurus
    :type list_of_thesauri: list(dict)
    :param list_of_thesauri:
    :return:
    """
    full_thesaurus = list_of_thesauri[0]
    for thesaurus in list_of_thesauri[1:]:
        for entry in thesaurus:
            if entry in full_thesaurus:
                # Ensure uniqueness
                full_thesaurus[entry] = list(set(thesaurus[entry] + full_thesaurus[entry]))
            else:
                full_thesaurus.update({entry: thesaurus[entry]})
    return full_thesaurus


def genFileThesaurus(sentences_list_location='Selection Texts.txt',
                     thesaurus_location='Thesauri/Synonyms.the',
                     thesaurus_type='synonyms'):
    """
    Stand-alone function to get a sentence set, and generate a list of thesaurus entries from it
    :param sentences_list_location:
    :param thesaurus_location:
    :param thesaurus_type:
    :return:
    """

    # Get a list of sentences (not a list of sentence sets)
    sentence_list = getSentences(sentences_list_location)
    sentence_list = [sentence for sentence_set in sentence_list for sentence in sentence_set]

    # Get a pre-made thesaurus if it already exists
    if os.path.isfile(thesaurus_location) is True:
        thesaurus = dict(ast.literal_eval(readFile(thesaurus_location)))
    else:
        thesaurus = {}

    # For each sentence
    for sentence in sentence_list:
        sentence = str(formatWordsList([sentence])[0])
        # Only add if not already within the thesaurus
        if sentence not in thesaurus:
            synonyms = getSynonyms(sentence.replace(' ', '_'), thesaurus_type)
            thesaurus.update({sentence: synonyms})

        # For each word within the sentence
        for word in sentence.strip().split(' '):
            if word not in thesaurus:
                synonyms = getSynonyms(word, thesaurus_type)
                thesaurus.update({word: synonyms})

    # Store the results
    writeFile(thesaurus_location, str(thesaurus).replace('],', '],\n').replace('{', '{\n').replace('}', '}\n'))

    # Return the thesaurus for further processing
    return thesaurus


def genFileSubDictionary(full_dictionary, dictionary_list, file_location='Dictionary.dict'):
    """
    Given a list of words and their phonemes, generate a file that can be referred back to later
    :type full_dictionary: dict
    :param full_dictionary:
    :type dictionary_list: dict
    :param dictionary_list:
    :param file_location:
    :return:
    """
    # Generate dictionary contents
    dictionary = ''
    for word in sorted(list(dictionary_list.keys())):
        i = 2
        # Add the word if it exists within the full dictionary
        if word not in full_dictionary:
            continue

        dictionary += str(word) + ' ' + str(full_dictionary[word]) + '\n'

        # Add other phonetic variations, if they exist
        while word + '({0})'.format(i) in full_dictionary:
            dictionary += str(word) + '({0})'.format(str(i)) + ' ' + str(full_dictionary[word]) + '\n'
            i += 1

    # Write contents to file
    writeFile(file_location, dictionary)


def genFileGrammar(grammar_name, grammar_rules, file_location, imports=None):
    """
    Given a list of grammar rules, generates a grammar file
    :param grammar_name:
    :param grammar_rules:
    :param file_location:
    :param imports:
    :return:
    """
    # Add the header
    grammar_file = '#JSGF V1.0;\n\ngrammar ' + str(grammar_name) + ';\n\n'

    # Add imports, if any
    if bool(imports) is True:
        for i in imports:
            grammar_file += 'import <' + str(i) + '.*>;\n'
        grammar_file += '\n'

    # Add grammar rules
    for rule in grammar_rules:
        if bool(rule) is True:
            grammar_file += 'public ' + str(grammar_rules[rule][0]) + '\n'
    grammar_file += '\n'

    # Create the grammar file
    writeFile(file_location, grammar_file)


def getSentenceSetSynonyms(sentence_set, full_thesaurus):
    """
    Provides a list of unique words, derived from all of the base words within
    the sentence set and their synonyms
    :param sentence_set:
    :param full_thesaurus:
    :return:
    """
    words_list = {}
    # For each sentence
    for sentence in sentence_set:
        # If a sentence doesn't exist within the thesaurus then add its word and skip the synonyms
        if sentence not in full_thesaurus:
            if sentence in words_list:
                words_list[sentence] += 1
            else:
                words_list.update({sentence: 1})
            continue

        # For each synonym within the sentence phrase
        for synonym in full_thesaurus[sentence]:
            if synonym in words_list:
                words_list[synonym] += 1
            else:
                words_list.update({synonym: 1})

        # For each word within the sentence
        for word in str(sentence).strip().split(' '):

            # For each synonym within the word
            for synonym in full_thesaurus[word]:
                if synonym in words_list:
                    words_list[synonym] += 1
                else:
                    words_list.update({synonym: 1})

    # Return the results
    return words_list


def getWordWeightings(sentences_list, full_thesaurus):
    """
    Provides a tally of how often a word appears between different sentence sets (document frequency)
    :param sentences_list:
    :param full_thesaurus:
    :return:
    """
    words_list = []

    # For each sentence set, generate a list of relevant words
    for sentence_set in sentences_list:
        words_list += [dict(getSentenceSetSynonyms(sentence_set, full_thesaurus))]

    word_tally = {}
    # For each word set, tally how often a word occurs
    for word_set in words_list:
        for word in word_set:
            if word in word_tally:
                word_tally[word] += 1
            else:
                word_tally.update({word: 1})

    # Return the words_list and tally
    return words_list + [word_tally]


def getRelevantSentenceSets(sentences_list, sentence_set_selections):
    """
    Determine which sentence sets are relevant by finding which sentence sets begin with one of the selections
    :param sentences_list:
    :param sentence_set_selections:
    :return:
    """
    sentences_sub_list = []
    for sentence_set in sentences_list:
        for selection in sentence_set_selections:
            if sentence_set[0] == selection:
                sentences_sub_list += [sentence_set]
                break

    return sentences_sub_list


def getTextWeighting(text, word_weights, confidence):
    """
    Find relevant words within the text and sum
    :param text:
    :param word_weights:
    :param confidence:
    :return:
    """
    # For each interesting word, generate a regular expression to find it
    # If found, add the words weighting to a tally for each sentence set the word is in
    # noinspection PyUnusedLocal
    selection_weighting = [0 for selection in word_weights[:-1]]

    for search_term in word_weights[-1]:
        # Generate the regular expression
        regex = genPhraseRegularExpression(search_term, True)

        # Search for the search term within the text
        if bool(re.findall(regex, text)) is True:
            # If it exists, add the weighting to the relevant selections
            for i in range(len(word_weights[:-1])):
                selection = word_weights[i]
                if search_term in selection:
                    selection_weighting[i] += 1.0 / word_weights[-1][search_term]

    # Finally, multiply the weightings by the confidence of the speech to text translation
    for i in range(len(selection_weighting)):
        selection_weighting[i] /= confidence
    return selection_weighting


# def makeSelection(text_confidence_pairs):
#     """
#     Given a set of textual inputs and their corresponding speech to text confidences, pick one
#     :param text_confidence_pairs:
#     :return:
#     """
    # a = text_confidence_pairs

    # Get the thesaurus
    # Get the text weightings


if __name__ == '__main__':
    test_text_ = "i erm i think vaguely should go break through a uh fucking door or something dude"

    dictionary_ = getDictionary()
    sentences_list_ = getSentences("Grammars/Selection Texts.txt")
    grammar_sentence_ = genSentenceGrammarRule(sentences_list_[0])
    thesaurus_ = {}
    thesaurus_ = mergeThesauri(
        [thesaurus_,
         genFileThesaurus("Grammars/Selection Texts.txt", "Thesauri/Synonyms.the", 'synonyms'),
         genFileThesaurus("Grammars/Selection Texts.txt", "Thesauri/Narrower.the", 'narrower'),
         genFileThesaurus("Grammars/Selection Texts.txt", "Thesauri/Related.the", 'related')]
    )
    # genFileSubDictionary(dictionary_, thesaurus_, 'Dictionaries/_master.dict')
    # genFileGrammar('Grammars/_test.gram', {'_test_': [grammar_sentence_]}, 'Grammars/_test.gram', ['words'])
    weightings_ = getWordWeightings(sentences_list_, thesaurus_)
    sentences_sub_list_ = getRelevantSentenceSets(sentences_list_, ['break the door down', 'continue', 'wake up'])

    weights_ = getTextWeighting(test_text_, weightings_, 1.0)

    selections_ = [selection[0] for selection in sentences_list_]
    selected_ = dict(zip(selections_, weights_))
    selected_ = [(k, selected_[k]) for k in sorted(selected_, key=selected_.get, reverse=True)]
    print(str(selected_).replace('),', '),\n'))


# Do for all text strings presented, and sum their values up respectively
# Select the max, or generate an error if:
#   Resultant coefficient has a small magnitude
#   0 or 2+ options are selected (still)




