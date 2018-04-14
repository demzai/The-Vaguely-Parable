"""
Given a file of sentences, generates a corresponding grammar file and regular expression
The grammar file is also constructed by finding a list of synonyms for each unique word from thesaurus.com
"""

# Dependencies:
import requests as req
import re
import num2words as nw
import os
import traceback as t
# import pocketsphinx


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
    "thank": ["thank"],
    "ta": ["ta"],
    "could": ["could"],
    "vaguely": ["vaguely"],
    "I'd": ["I'd"],
    "can": ["can"]
}


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
            # word = str(word).replace('_', ' ').replace('-', ' ').replace('\'', '')
            return_list += [word]
    return return_list


def getSynonyms(word):
    """
    For a given word, searches for synonyms on both thesaurus.com and powerthesaurus.org
    :param word:
    :return:
    """
    word_set = {formatWordsList([word])[0]: 0}

    # Get "narrower" words from http://powerthesaurus.org
    try:
        site = req.get('http://powerthesaurus.org/' + word + '/narrower').text
        discovered = re.findall('class="pt-thesaurus-card__term-title"><a href="/(.*)/narrower"', site)
        for i in formatWordsList(discovered):
            word_set.update({i: 0})
    except OSError as e:
        print('Failed to load site 2 HTTP resource, {0}'.format(e))

    # Get synonyms from http://powerthesaurus.org
    if len(word_set) is 0:
        try:
            site = req.get('http://powerthesaurus.org/' + word + '/synonyms').text
            discovered = re.findall('class="pt-thesaurus-card__term-title"><a href="/(.*)/synonyms"', site)
            for i in formatWordsList(discovered):
                word_set.update({i: 0})
        except OSError as e:
            print('Failed to load site 2 HTTP resource, {0}'.format(e))

    # Get related words from http://powerthesaurus.org
    try:
        site = req.get('http://powerthesaurus.org/' + word + '/related').text
        discovered = re.findall('class="pt-thesaurus-card__term-title"><a href="/(.*)/related"', site)
        for i in formatWordsList(discovered):
            word_set.update({i: 0})
    except OSError as e:
        print('Failed to load site 2 HTTP resource, {0}'.format(e))

    return list(word_set.keys())


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


def writeGrammarFile(file_location, grammar_name, grammar_rules, imports=None):
    """
    Auto-generates a grammar file when given a set of grammar rules etc.
    :param file_location:
    :param grammar_name:
    :param grammar_rules:
    :param imports:
    :return:
    """
    with open(file_location, 'w') as grammar_file:
        # Add the grammar name
        grammar_file.write("#JSGF V1.0;\n\ngrammar " + str(grammar_name) + ';\n\n')

        # Add imports, if any
        if imports is not None:
            for i in imports:
                grammar_file.write('import <' + str(i) + '.*>;\n')
            grammar_file.write('\n')

        # Add grammar rules
        for rule in grammar_rules:
            if rule == '' or rule is None:
                continue
            grammar_file.write('public ' + str(grammar_rules[rule][0]) + ' // ' + str(grammar_rules[rule][1]) + '\n')
        grammar_file.write('\n')

    return


# noinspection SpellCheckingInspection
def getDictionary():
    """
    Extracts the model dictionary, allowing testing for word inclusion
    :return:
    """
    # dictionary = readFile(pocketsphinx.get_model_path() + '/cmudict-en-us.dict')
    dictionary = readFile('C:/Program Files/Python35/Lib/site-packages/speech_recognition/pocketsphinx-data/en-US' + \
                          '/pronounciation-dictionary.dict')
    return re.sub(' .*\n', '\n', dictionary).split('\n')


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
    for sentences in sentence_sets:
        for sentence in sentences:
            # Include phrases
            unique_words.update({sentence.replace(' ', '_'): []})
            for word in sentence.split(' '):
                unique_words.update({word: []})
    return unique_words


def getSynonymsForAllWords(unique_words):
    """
    Automatically acquire all synonyms for all words generated
    Ensure each synonym phrases uniqueness & validity within the dictionary
    :param unique_words:
    :return:
    """
    # Get synonyms for each word
    for word in unique_words:
        if word is '':
            continue
        # Get synonyms
        if __name__ == '__main__':
            print(word)
        # Odd error where the site formatting changes and gives 0 results back... just try it a second time to be sure
        synonyms = getSynonyms(word)

        # Determine if each synonym / phrase is fully described from the dictionary, if not then ignore it
        word_list = []
        dictionary = getDictionary()
        for phrase in synonyms:
            is_good = True
            for phrase_word in phrase.split(' '):
                if phrase_word not in dictionary:
                    is_good = False
                    print('WARNING: "{0}" has been ignored, '.format(phrase) + \
                          '"{0}" was not found in the word model.'.format(phrase_word))
                    break
            if is_good is True:
                word_list += [phrase]

        # Store the result
        if __name__ == '__main__':
            print(str(word_list))
        unique_words[word] += word_list
    return unique_words


def genGrammarsForWords(unique_words):
    """
    Generate grammar rules for each unique word
    :param unique_words:
    :return:
    """
    word_grammar_rules = {}
    for word in unique_words:
        # Create a single, unified list of synonyms
        synonyms = []

        for i in unique_words[word]:
            synonyms += [i]

        if len(synonyms) is 0:
            continue

        # Create a grammar rule
        rule = '<' + word + '> = ( '
        regex = '('
        for synonym in synonyms:
            synonym = synonym.replace('_', ' ')
            rule += str(synonym) + ' | '
            regex += str(synonym) + '|'
        rule = rule[:-3] + ' );'
        regex = regex[:-1] + ')'
        word_grammar_rules.update({word: [rule, regex]})
    return word_grammar_rules


def genGrammarsForSentenceSets(sentence_sets, word_grammar_rules, inflexion_rules=None):
    """
    Generate grammar rules for each set of sentences, based on the grammar rules generated for each word
    :param sentence_sets:
    :param word_grammar_rules:
    :param inflexion_rules:
    :return:
    """
    # Initialise
    if inflexion_rules is not None:
        sets_of_grammar_rules = inflexion_rules
    else:
        sets_of_grammar_rules = {}

    # For each sentence set
    for i in range(len(sentence_sets)):
        sentence_set = sentence_sets[i]
        sentence_id = sentence_set[0].replace(' ', '')
        # Open up a new grammar rule and regex definition
        grammar_rule = '<' + str(sentence_id) + '> = '
        regex_rule = ''
        for j in range(1, len(sentence_set)):
            sentence = sentence_set[j]
            # Open up another possible sentence match
            grammar_rule += '( '
            regex_rule += '('
            for word in sentence.split(' '):
                if word == '':
                    continue
                # Insert each word of the sentence, along with a space afterwards
                if inflexion_rules is None:
                    grammar_rule += '<' + word + '> '
                    regex_rule += word_grammar_rules[word][1] + ' '
                else:
                    grammar_rule += '<inflexions> <' + word + '> '
                    regex_rule += inflexion_rules['inflexions'][1] + word_grammar_rules[word][1] + ' '
            # Close off the sentence possibility, leaving the option for another one to come after
            if inflexion_rules is None:
                grammar_rule += ') | '
                regex_rule = regex_rule[:-1] + ')|'
            else:
                grammar_rule += '<inflexions> ) | '
                regex_rule = regex_rule[:-1] + inflexion_rules['inflexions'][1] + ')|'
        # Close off the sentence set and add to the rules list
        grammar_rule = grammar_rule[:-3] + ';'
        regex_rule = regex_rule[:-1]
        # Make the first sentence in the list the ID for
        sets_of_grammar_rules.update({sentence_id: [grammar_rule, regex_rule]})
    return sets_of_grammar_rules


# noinspection PyBroadException
def genGrammarForSelectionSet(selections, grammar_name):
    """
    Given a list of narrative selections, find their corresponding grammars and generate
        a meta-grammar to search for all of them
    :param selections:
    :param grammar_name:
    :return:
    """
    # Find valid selections
    valid = []
    regex_map = {}
    for selection in selections:
        shorthand = str(selection).replace('_', '')
        file = grammar_directory + shorthand + '.gram'
        try:
            if os.path.isfile(file) is True:
                grammar = readFile(file)
                regex_map.update({selection: '(' + re.findall('// (.+)\n', grammar)[0] + ')'})  # Crash if none found
                valid += [shorthand]
        except Exception:
            continue

    # Create a grammar using the valid selections
    grammar_rule = '<' + str(grammar_name) + '> = ( <'
    for selection in valid:
        grammar_rule += str(selection) + '> | <'
    grammar_rule = grammar_rule[:-4] + ' );'

    # Create grammar file for the grammar
    writeGrammarFile(grammar_directory + str(grammar_name) + '.gram',
                     str(grammar_name), {str(grammar_name): [grammar_rule, 'N/A']}, valid)

    # Return the file directory and name, as well as the respective parent grammar files
    return [grammar_directory + str(grammar_name) + '.gram', regex_map]


# noinspection PyBroadException
def cleanupGrammarFile(grammar_name):
    """
    Delete extraneous files to prevent file spamming
    :param grammar_name:
    :return:
    """
    with open("log_file.txt", "a") as log_file:
        log_file.write('Cleaning up: ' + str(grammar_name) + '\n')
    # Remove the grammar file (.gram)
    try:
        os.remove(grammar_directory + str(grammar_name) + '.gram')
    except Exception:
        pass
    # Remove the phoneme file (.fsg)
    try:
        os.remove(grammar_directory + str(grammar_name) + '.fsg')
    except Exception:
        pass
    # Remove the dictionary file (.dict)
    try:
        os.remove(dictionary_directory + str(grammar_name) + '.fsg')
    except Exception:
        pass


def main():
    """
    Main process for generating grammar files
    :return:
    """
    inflexion_sets = getSentences(grammar_directory + "Inflexions.txt")
    inflexion_grammar = genGrammarsForWords(inflexions)
    inflexion_rules = genGrammarsForSentenceSets(inflexion_sets, inflexion_grammar)
    inflexion_rules['inflexions'][0] = '{0} ]'.format(inflexion_rules['inflexions'][0]).replace('(', '[', 1)
    inflexion_rules['inflexions'][0] = inflexion_rules['inflexions'][0].replace('( ', '').replace(' )', '')
    inflexion_rules['inflexions'][1] = inflexion_rules['inflexions'][1].replace('((', '').replace('))', '')
    inflexion_rules['inflexions'][1] = '[{0}]? ?'.format(inflexion_rules['inflexions'][1])
    if __name__ == '__main__':
        print(inflexion_rules)

    sentence_sets = getSentences(grammar_directory + "Selection Texts.txt")
    unique_words = getUniqueWords(sentence_sets)
    unique_words = getSynonymsForAllWords(unique_words)

    word_grammar_rules = genGrammarsForWords(unique_words)
    writeGrammarFile(grammar_directory + "words.gram", 'words', word_grammar_rules)
    sentence_set_grammar_rules = genGrammarsForSentenceSets(sentence_sets, word_grammar_rules, inflexion_rules)

    for rule in sentence_set_grammar_rules:
        if rule == '':
            continue
        if __name__ == '__main__':
            print('Generating: ' + str(rule) + '.gram')
        sentence_rule = {rule: sentence_set_grammar_rules[rule]}
        writeGrammarFile(grammar_directory + str(rule) + ".gram", str(rule), sentence_rule, ['words'])


if __name__ == '__main__':
    main()



