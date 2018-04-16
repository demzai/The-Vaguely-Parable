# """
# # This is the testing ground.
# # Develop functions here, but do not leave them here!
# # This is a glorified playground to make a mess in!
# """

# Dependencies:
import requests as req
import re
import num2words as nw
import pocketsphinx
from multiprocessing.dummy import Pool as ThreadPool
import time as t


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


def getSynonyms(word, type='synonyms'):
    """
    For a given word, searches for synonyms on both thesaurus.com and powerthesaurus.org
    :param word:
    :return:
    """
    print(str(word))
    word_set = {formatWordsList([word])[0]: 0}
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 ' +
                      '(KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
    url = 'http://powerthesaurus.org/' + word + '/' + type

    # Get synonyms from http://powerthesaurus.org
    try:
        r = req.get(url, headers=headers, timeout=10)
        t.sleep(2)
        site = r.text
        discovered = re.findall('class="pt-thesaurus-card__term-title"><a href="/(.*)/' + type + '"', site)
        for i in formatWordsList(discovered):
            word_set.update({i: 0})
    except OSError as e:
        print('Failed to load site 2 HTTP resource, {0}'.format(e))

    print(str(word_set))
    return '"' + str(word) + '" : "' + str(list(word_set.keys())) + '"\n'


def readFile(file_location):
    """
    Generic, simplified, function to extract the contents of a file
    :param file_location:
    :return:
    """
    with open(file_location, 'r') as fileObject:
        fileContents = fileObject.read()
    return fileContents


def getDictionary():
    """
    Extracts the model dictionary, allowing testing for word inclusion
    :return:
    """
    dictionary = readFile(pocketsphinx.get_model_path() + '/cmudict-en-us.dict')
    return re.sub(' .*\n', '\n', dictionary).split('\n')


# function to be mapped over
def calculateParallel(words, threads=2):
    pool = ThreadPool(threads)
    results = pool.map(getSynonyms, words)
    pool.close()
    pool.join()
    return results


if __name__ == "__main__":
    words = getDictionary()[:3861]
    t1 = t.time()
    synonyms = calculateParallel(words, 3861)
    synonyms = sorted(synonyms)
    for word in synonyms:
        # synonyms = getSynonyms(word, 'synonyms')
        # narrow = getSynonyms(word, 'narrow')
        # related = getSynonyms(word, 'related')
        with open('thesaurus_synonyms', 'a') as fileObject:
            fileObject.write(str(word))
        # with open('thesaurus_narrow', 'a') as fileObject:
        #     fileObject.write(str(word) + ' : ' + str(narrow))
        # with open('thesaurus_related', 'a') as fileObject:
        #     fileObject.write(str(word) + ' : ' + str(related))
    t2 = t.time()
    print(t1)
    print(t2)
    print(t2-t1)

