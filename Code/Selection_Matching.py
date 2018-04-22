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
thesaurus_directory = "Thesauri/"
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
    "tah": ["tah"],
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
            if '%' in i or len(i) <= 2:
                continue

            # Add the word or phrase into the thesaurus
            word_set.update({i: 0})

    # If failed, then provide an error message
    except OSError as e:
        print('Failed to load site HTTP resource, {0}'.format(e))

    # Return a list of unique words and phrases associated with the provided word
    return list(word_set.keys())


def validDictionary(list_of_phrases, full_dictionary):
    """
    Given some words, test if they're in the dictionary or not and return only the valid ones
    :param list_of_phrases:
    :param full_dictionary:
    :return:
    """
    valid = []
    for phrase in list_of_phrases:
        is_good = True
        for word in phrase.split(' '):
            if word not in full_dictionary:
                is_good = False
                break
        if is_good is True:
            valid += [phrase]
    return valid


def genPhraseRegularExpression(phrase, is_whole_only=True):
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


def genPhraseGrammarRule(phrase, full_dictionary, thesaurus, add_inflexions=True):
    """
    Given a textual phrase, generate a grammar rule for it
    :param thesaurus:
    :param full_dictionary:
    :param add_inflexions:
    :type phrase: str
    :param phrase:
    :return:
    """
    # Check for an empty condition
    phrase = phrase.strip()
    if bool(phrase) is False:
        return {}

    # Create a sub-thesaurus containing only words existing within the dictionary related to words in the phrase
    phrase_list = []
    if phrase in thesaurus:
        phrase_list = validDictionary(thesaurus[phrase], full_dictionary)
    elif phrase in inflexions:
        phrase_list = inflexions[phrase]
    if bool(phrase_list) is False:
        return {}

    # Determine the appender, which can add inflexions in before and after every word if so desired
    appender = ['', '']
    if add_inflexions is True:
        appender[0] = '(<inflexions>)* '
        appender[1] = '(.*)? ?'
        # for inflexion in inflexions:
        #     appender[1] += inflexion + '|'
        # appender[1] = appender[1][:-1] + ')* ?'

    # Create rule title and beginning gumph
    name = phrase.replace('_', '').replace('-', '').replace(' ', '')
    rule = 'public <{0}> = ( {1}'.format(name, appender[0])
    regex = '('

    # Add each valid variant of the phrase to te grammar rule
    for sub_phrase in phrase_list:
        rule += '( '
        regex += '('
        for word in sub_phrase.strip().split(' '):
            rule += '{0} {1}'.format(str(word), appender[0])
            regex += '{0} ?{1} '.format(str(word), appender[1])
        rule += ') | '
        regex = regex[:-1] + ')|'

    # Close off the rule and return it
    rule = rule[:-2] + ')'
    regex = regex[:-1] + ')'

    return {phrase: [rule, regex]}


def genSentenceGrammarRule(sentence_set):
    """
    Creates a grammar rule for a given list of sentences
    :type sentence_set: list
    :param sentence_set:
    :return:
    """
    if bool(sentence_set) is False:
        return ''

    rule = 'public <' + sentence_set[0].replace(' ', '') + '> = '
    # Make each word reference another grammar rule, and consider each sentence via an OR statement
    for sentence in sentence_set[1:]:
        rule += '( <{0}> ) | '.format(str(sentence).strip().replace(' ', '> <'))
    rule = rule[:-2]

    return rule


def genSentenceGrammarRegex(sentence_set, word_rules):
    """
    Generates a regular expression for the given sentence set
    Based on the words used and their regular expressions
    :param sentence_set:
    :param word_rules:
    :return:
    """
    # Open the regex
    regex = '('
    for sentence in sentence_set:
        # Create a new search group for each sentence
        regex += '('
        # Add the word rules instead of the actual words if possible
        for word in sentence.strip().split(' '):
            if word in word_rules:
                regex += word_rules[word][1]
            else:
                regex += str(word)
            regex += ' '
        # Prepare for another sentence
        regex = regex[:-1] + ')|'
    # Close off the regex
    regex = regex[:-1] + ')'
    return regex


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


def genFileSubDictionary(full_dictionary, thesaurus, file_location='Dictionary.dict'):
    """
    Given a list of words and their phonemes, generate a file that can be referred back to later
    :type full_dictionary: dict
    :param full_dictionary:
    :type thesaurus: dict
    :param thesaurus:
    :param file_location:
    :return:
    """
    # Generate a words list
    words_list = {}
    for keyword in thesaurus:
        for phrase in thesaurus[keyword]:
            for word in phrase.split(' '):
                words_list.update({word: 0})

    # Generate dictionary contents
    dictionary = ''
    for word in sorted(list(words_list.keys())):
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
    rule_set = sorted(list(grammar_rules.keys()))
    for rule in rule_set:
        if bool(rule) is True:
            grammar_file += '{0} // {1}\n'.format(str(grammar_rules[rule][0]), str(grammar_rules[rule][1]))

    # Create the grammar file
    writeFile(file_location, grammar_file)


# noinspection PyBroadException
def cleanupExcessFiles(file_id):
    """
    Delete extraneous files to prevent file spamming
    :param file_id:
    :return:
    """
    with open("log_file.txt", "a") as log_file:
        log_file.write('Cleaning up: ' + str(file_id) + '\n')
    # Remove the grammar file (.gram)
    try:
        os.remove(grammar_directory + str(file_id) + '.gram')
    except Exception:
        pass
    # Remove the phoneme file (.fsg)
    try:
        os.remove(grammar_directory + str(file_id) + '.fsg')
    except Exception:
        pass
    # Remove the dictionary file (.dict)
    try:
        os.remove(thesaurus_directory + str(file_id) + '.dict')
    except Exception:
        pass


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
    sentences_titles = []

    # For each sentence set, generate a list of relevant words
    for sentence_set in sentences_list:
        words_list += [dict(getSentenceSetSynonyms(sentence_set, full_thesaurus))]
        sentences_titles += [sentence_set[0]]

    word_tally = {}
    # For each word set, tally how often a word occurs
    for word_set in words_list:
        for word in word_set:
            if word in word_tally:
                word_tally[word] += 1
            else:
                word_tally.update({word: 1})

    # Return the words_list and tally
    return dict(zip(sentences_titles + ['__all__'], words_list + [word_tally]))


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


def getTextWeighting(text, word_weightings, confidence):
    """
    Find relevant words within the text and sum
    :param text:
    :param word_weightings:
    :param confidence:
    :return:
    """
    # For each interesting word, generate a regular expression to find it
    # If found, add the words weighting to a tally for each sentence set the word is in
    selection_weighting = dict(zip(list(word_weightings.keys()), [0 for _ in range(len(word_weightings))]))
    selection_weighting.pop('__all__', None)

    for search_term in word_weightings['__all__']:
        # Generate the regular expression
        regex = genPhraseRegularExpression(search_term, True)

        # Search for the search term within the text
        if bool(re.findall(regex, text)) is True:
            # If it exists, add the weighting to the relevant selections
            for i in word_weightings:
                if i == '__all__':
                    continue
                if search_term in word_weightings[i]:
                    weight = word_weightings[i][search_term] / word_weightings['__all__'][search_term]
                    with open("log_file.txt", "a") as log_file:
                        log_file.write('\t{0} : {1} : {2} : {3}\n'.format(
                            str(text), str(search_term), str(weight), str(i)))
                    selection_weighting[i] += weight

    # Finally, multiply the weightings by the confidence of the speech to text translation
    for i in selection_weighting:
        selection_weighting[i] *= confidence
    return selection_weighting


weightings = dict(ast.literal_eval(readFile(thesaurus_directory + 'Weightings.weight')))


def makeSubDictionary(narrative_selections, file_location):
    """
    Given a selection set, generate a dictionary of all words included within those sentence sets
    :param narrative_selections:
    :param file_location:
    :return:
    """
    # Get the words list
    global weightings
    thesaurus = {}
    for key_ in weightings:
        if key_ == '__all__':
            continue
        for selection in narrative_selections:
            if selection == key_:
                thesaurus.update(weightings[key_])
    thesaurus = {0: list(thesaurus.keys())}

    # Generate the mini-dictionary
    genFileSubDictionary(getDictionary(), thesaurus, file_location)


def matchRegex(text, regex_map):
    """
    Given a textual input and a set of regular expressions, find results within the text
    :param text:
    :param regex_map:
    :return:
    """
    matches = []
    if text[1] > confidence_threshold:
        # Use regex's to select a narrative
        for regex in regex_map:
            # Search for the regex within the resulting file to ID which grammar found it
            if len(re.findall(regex_map[regex], text[0])) is not 0:
                matches += [regex]
    return matches


def makeSelectionRegex(texts, regex):
    """
    Makes the selection via the use of regular expressions made via grammars
    :param texts:
    :param regex:
    :return:
    """
    # Find matching regular expressions within the translated texts
    matches = []
    for i in range(len(texts)):
        matches += [matchRegex(texts[i], regex)]

    # Determine which narrative to select
    # Check for successful results first:
    if len(matches[0]) is 1:
        output = [matches[0][0], matches[0]]
    elif len(matches[1]) is 1:
        output = [matches[1][0], matches[1]]
    elif len(matches[2]) is 1:
        output = [matches[2][0], matches[2]]
    # Assume creator error if any have more than 1 match
    elif len(matches[0]) >= 2 or len(matches[1]) >= 2 or len(matches[2]) >= 2:
        output = ['$Creator_Error', [matches[0], matches[1], matches[2]]]
    # Else assume that the user has made an error
    else:
        output = ['$User_Error', []]
    return output


def makeSelectionMetric(text_confidence_pairs, selection_set):
    """
    Given a set of textual inputs and their corresponding speech to text confidences, pick one
    :param text_confidence_pairs:
    :param selection_set:
    :return:
    """
    # Pick out the relevant selections
    global weightings
    sub_weightings = {}
    metric_weightings = {}
    for key_ in weightings:
        if key_ == '__all__':
            continue
        for selection in formatWordsList(selection_set):
            if selection == key_:
                sub_weightings.update({selection: weightings[selection]})
                metric_weightings.update({selection: 0})
    sub_weightings.update({'__all__': weightings['__all__']})
    # print(str(selection_set) + '\n' + str(sub_weightings))

    # Get the weightings for each word, confidence pair
    for pair in text_confidence_pairs:
        word_weights = getTextWeighting(pair[0], sub_weightings, pair[1])
        for i in metric_weightings:
            metric_weightings[i] += word_weights[i]

    # Sort the results based on their selection metric and return the selection priority list
    selected = [(k, metric_weightings[k]) for k in sorted(metric_weightings, key=metric_weightings.get, reverse=True)]
    return [str(selected[0][0]).replace(' ', '_'), selected]


def makeSelection(text_confidence_pairs, selection_set, regex):
    """
    Attempt to make a selection via a metric based on the words used
    If that fails, default to the regular expression approach, assuming an underlying grammar is present
    :param text_confidence_pairs:
    :param selection_set:
    :param regex:
    :return:
    """
    # Get both for debugging purposes
    metric = makeSelectionMetric(text_confidence_pairs, selection_set)
    weighted_results = metric[1]
    with open("log_file.txt", "a") as log_file:
        log_file.write(str(metric))

    # If the metric-based approach fails, then attempt to select via regular expressions
    if float(weighted_results[0][1]) * 0.9 < float(weighted_results[1][1]) or float(weighted_results[0][1]) < 0.1:
        return makeSelectionRegex(text_confidence_pairs, regex)
    # Otherwise, return the find as is
    else:
        return metric


def getUniqueWords(sentences_list):
    """
    Given a set of sentences, generate a list of unique words used within them
    :param sentences_list:
    :return:
    """
    unique_words = {}
    # For each set of sentences
    for sentence_set in sentences_list:
        words = {}
        # For each sentence within that set
        for j in range(1, len(sentence_set)):
            sentence = sentence_set[j]
            words.update({sentence.replace(' ', '_'): []})
            # For each word within the sentence
            for word in sentence.replace('-', ' ').replace('_', ' ').split(' '):
                # Add to a map to remove duplicates
                words.update({word: []})
        # Store the result
        unique_words.update({sentence_set[0]: list(words.keys())})
    return unique_words


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

    # # Create a grammar using the valid selections
    # grammar_rule = '<' + str(grammar_name) + '> = ( <'
    # for selection in valid:
    #     grammar_rule += str(selection) + '> | <'
    # grammar_rule = grammar_rule[:-4] + ' );'

    # Create grammar file for the grammar
    # genFileGrammar(grammar_name, {str(grammar_name): [grammar_rule, 'N/A']},
    #                grammar_directory + str(grammar_name) + '.gram', valid)

    # Return the file directory and name, as well as the respective parent grammar files
    return [grammar_directory + str(grammar_name) + '.gram', regex_map]


def main():
    """
    Function to be run to generate preliminary files, such as dictionaries and grammars
    :return:
    """
    # #################### DICTIONARIES #####################
    # Initialise by generating a thesaurus, dictionary and words-list
    selection_list_location = thesaurus_directory + "Selection Texts.txt"
    thesaurus = mergeThesauri(
        [genFileThesaurus(selection_list_location, "Thesauri/Synonyms.the", 'synonyms'),
         genFileThesaurus(selection_list_location, "Thesauri/Narrower.the", 'narrower'),
         genFileThesaurus(selection_list_location, "Thesauri/Related.the", 'related')]
    )
    full_dictionary = getDictionary()
    sentences_list = getSentences(selection_list_location)
    unique_words = getUniqueWords(sentences_list)

    # Create a dedicated file for the weightings to prevent accidental changes to the thesaurus files
    weightings_ = getWordWeightings(getSentences(thesaurus_directory + "Selection Texts.txt"), thesaurus)
    with open(thesaurus_directory + "Weightings.weight", "w") as log_file:
        log_file.write(str(weightings_))

    # For each set of unique words, generate a sub-dictionary file
    for sub_list in unique_words:
        # print(sub_list + ':')

        # Generate a temporary thesaurus that is a subset of the original
        sub_thesaurus = {}
        sub_thesaurus.update(inflexions)
        for word in unique_words[sub_list]:
            sub_thesaurus.update({word: thesaurus[formatWordsList([word])[0]]})

        # Generate the dictionary file
        genFileSubDictionary(full_dictionary, sub_thesaurus,
                             str(dictionary_directory) + str(sub_list).replace(' ', '') + '.dict')

    # #################### GRAMMARS #####################
    # Create grammar rules for each of the thesaurus entries
    grammar_word_rules = {}
    for inflexion in inflexions:
        grammar_word_rules.update(genPhraseGrammarRule(inflexion, full_dictionary, thesaurus, False))
    for word in thesaurus:
        grammar_word_rules.update(genPhraseGrammarRule(word, full_dictionary, thesaurus, True))

    # Add the rule for inflexions to the words grammar rules list
    inflexion_setup = ['inflexions'] + list(inflexions.keys())
    grammar_word_rules.update({str(inflexion_setup).replace(' ', '').replace('_', '').replace('-', ''): [
        genSentenceGrammarRule(inflexion_setup), genSentenceGrammarRegex(inflexion_setup, grammar_word_rules)]})

    # Generate rules for each sentence set
    grammar_rules = {}
    for sentence_set in sentences_list:
        grammar_rules.update({str(sentence_set[0]).replace(' ', '').replace('_', '').replace('-', ''): [
            genSentenceGrammarRule(sentence_set), genSentenceGrammarRegex(sentence_set, grammar_word_rules)]})

    # Create grammar rules files, one for all the thesaurus entries and one per sentence grammar
    genFileGrammar('words', grammar_word_rules, grammar_directory + 'words.gram')
    for rule in grammar_rules:
        genFileGrammar(rule, {rule: grammar_rules[rule]}, grammar_directory + rule + '.gram', ['words'])


if __name__ == '__main__':
    main()
    # test_text_ = [
    #     ['look for others', 0.97110075, ''],
    #     ['look for others', 0.7, ''],
    #     ['look full of those', 0.2104472870771945, '']
    # ]
    #
    # # Grab real-world data to fill these slots! (Can be obtained from Selector.py lines 288 and 289)
    # regex_map_ = {}
    # options_ = []
    #
    # sentences_list_ = getSentences(grammar_directory + "Selection Texts.txt")
    # thesaurus_ = mergeThesauri(
    #     [
    #         genFileThesaurus("Grammars/Selection Texts.txt", "Thesauri/Synonyms.the", 'synonyms'),
    #         genFileThesaurus("Grammars/Selection Texts.txt", "Thesauri/Narrower.the", 'narrower'),
    #         genFileThesaurus("Grammars/Selection Texts.txt", "Thesauri/Related.the", 'related')
    #     ]
    # )
    #
    # selected_ = makeSelection(test_text_, options_, regex_map_)
    # print(str(selected_).replace('),', '),\n').replace('},', '},\n').replace('],', '],\n'))

