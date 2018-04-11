"""
The code presented focuses on converting spoken words into textual data for further processing.
It provides a speech to text service that can  run independently from the rest of the system.
The code here is intended to be called as a child process... thread safety rules apply.
Use protection, get consent, and play nice kids!
"""

# Dependencies:
import Sentence_Converter as sc
import speech_recognition as sr
import multiprocessing as mp
import os
import re


def readSphinxData(sphinx_data, error):
    """
    Given an object returned from sphinx, convert it into a single result and its confidence level
    :param sphinx_data:
    :param error:
    :return:
    """
    if error != '' or sphinx_data is None or sphinx_data == []:
        return ['', 0, error]

    top_10 = [[best.hypstr, best.score] for best, k in zip(sphinx_data.nbest(), range(10))]
    # segments = [seg.word for seg in sphinx_data.seg()]
    confidence = sphinx_data.get_logmath().exp(sphinx_data.hyp().prob)
    return [top_10[0][0], confidence, error]  # [Top Result, Confidence, Error]


def readGoogleData(google_data, error):
    """
    Given an object returned from google, convert it into a single result and its confidence level
    :param google_data:
    :param error:
    :return:
    """
    if error != '' or google_data is None or google_data == []:
        return ['', 0, error]

    return [google_data['alternative'][0]['transcript'],
            google_data['alternative'][0]['confidence'],
            error]  # [Top Result, Confidence, Error]


# noinspection PyUnusedLocal,PyBroadException
def getSphinxTranslation(audio, result, grammar=None):
    """
    Given an audio snippet, and maybe some grammar, convert the speech into text using CMUsphinx
    :param audio:
    :param result:
    :type result: mp.Manager().list
    :param grammar:
    :return:
    """
    converter = sr.Recognizer()
    translation = None
    error = ''
    try:
        # Translate with or without grammar
        if grammar is not None:
            translation = converter.recognize_sphinx(audio, show_all=True, grammar=grammar)
        else:
            translation = converter.recognize_sphinx(audio, show_all=True)
    except sr.UnknownValueError:
        error = 'Bad Recognition'
    except Exception:
        error = 'Failed Server Request'
    finally:
        # Return only the data of interest
        translation = readSphinxData(translation, error)
        for i in range(3):
            result[i] = translation[i]
        return result


# noinspection PyUnusedLocal, PyBroadException
def getGoogleTranslation(audio, result):
    """
    Given an audio snippet, and maybe some grammar, convert the speech into text using Google
    :param audio:
    :param result:
    :type result: mp.Manager().list
    :return:
    """
    converter = sr.Recognizer()
    translation = None
    error = ''
    try:
        # Translate the audio into text
        translation = converter.recognize_google(audio, show_all=True)
        if translation is []:
            error = 'Bad Recognition'
    except sr.UnknownValueError:
        error = 'Bad Recognition'
    except Exception:
        error = 'Failed Server Request'
    finally:
        # Return only the information of interest
        translation = readGoogleData(translation, error)
        for i in range(3):
            result[i] = translation[i]
        return result


# noinspection PyBroadException,PyUnusedLocal
def selector(inputs, outputs, lock_outputs, is_faulty):
    """
    Takes an audio file and narrative list in, and converts them into a narrative selection
    Generates a grammar file & related regex list based on the possible narrative statements
    Performs speech to text using both CMUsphinx (offline) and Google, via separate processes
    Cleans up the generated grammar file to prevent file spamming
    Uses regex list to determine the selected narrative, or selection error

    :param inputs: [audio, narratives]
    :param outputs: [sphinx result, google result, narrative selection, is_finished]
    :param lock_outputs: multi-processing protection
    :param is_faulty: fail-safe return message
    :return:
    """
    # Extract the inputs
    audio = inputs[0]
    narratives = inputs[1]
    process_id = os.getpid()
    grammar_file = None
    regex_map = {}  # @todo double check if needed
    result_sphinx = ['', 0, '']
    result_google = ['', 0, '']

    # Throw everything inside of a try except loop to call all errors
    try:
        # If the admin made a boo boo, then give him a firm warning
        if isinstance(narratives, list) is False and narratives is not None:
            raise TypeError('"narratives" IS NOT A LIST!')

        # Get grammars and regex's
        elif narratives is not None and len(narratives) is not 0:
            # Get a list of narrative names
            narrative_names = [x[0] for x in narratives]
            [grammar_file, regex_map] = sc.genGrammarForSelectionSet(narrative_names, process_id)

        # Convert the audio using CMUsphinx (offline) and Google (online)
        if True:
            result_sphinx = mp.Manager().list(['', 0, ''])
            result_google = mp.Manager().list(['', 0, ''])
            process_sphinx = mp.Process(target=getSphinxTranslation, args=(audio, result_sphinx, grammar_file))
            process_google = mp.Process(target=getGoogleTranslation, args=(audio, result_google))
            process_sphinx.start()
            process_google.start()
            process_sphinx.join()
            process_google.join()
            with lock_outputs:
                outputs[0] = [x for x in result_sphinx]
                outputs[1] = [x for x in result_google]
        sc.cleanupGrammarFile(process_id)  # Remove excess file baggage

        # If the Google result gave a bad recognition error then ignore the whole thing
        if result_google[2] == 'Bad Recognition':
            with lock_outputs:
                outputs[2] = ['$Ignore', []]
                outputs[-1] = True
            return

        # Deduce if its worth running regex's
        matches = []
        if result_sphinx[1] > sc.confidence_threshold:
            # Use regex's to select a narrative
            for regex in regex_map:
                # Search for the regex within the resulting file to ID which grammar found it
                if len(re.findall(regex_map[regex], result_sphinx[0])) is not 0:
                    matches += regex
                    # @todo insert break when not testing?

        # Attempt to resolve via a language model, if needed
        if len(matches) is 0 and result_google[1] > sc.confidence_threshold:
            for regex in regex_map:
                # Search for the regex within the resulting file to ID which grammar found it
                if len(re.findall(regex_map[regex], result_google[0])) is not 0:
                    matches += regex
                    # @todo insert break when not testing?

        # Determine which narrative to select
        with lock_outputs:
            # Check for a "user error" - speech to text failed or user said something incorrect
            if len(matches) is 0:
                outputs[2] = ['$User_Error', matches]
                outputs[-1] = True
            # Check for creator error - creator has specified a similar sentence (inc. synonyms) for two selections
            elif len(matches) >= 2:
                outputs[2] = ['$Creator_Error', matches]
                outputs[-1] = True
            # Return the users selection
            else:
                outputs[2] = [matches[0], matches]
                outputs[-1] = True
        return

    # On exception: print cause, or skip entirely
    except Exception as e:
        print('Selector Error: {0}'.format(e))
        pass
    # Ensure the faulty flag is raised on an error, no matter what
    finally:
        # noinspection PyUnusedLocal
        is_faulty = True


class SelectorObj:
    """
    Object to handle the interface to a selector
    """
    def __init__(self, audio_to_convert, audio_timestamp, narrative_options):
        # Initialise the inputs
        self.audio = audio_to_convert
        self.timestamp = audio_timestamp
        self.narratives = narrative_options
        self.__inputs = [audio_to_convert, narrative_options]  # audio, narrative_options

        # Initialise the outputs
        self.is_finished = False
        self.result_sphinx = None
        self.result_google = None
        self.selected_narrative = None
        self.__outputs = mp.Manager().list(
            ['', '', [], False])  # sphinx results, google results, selected narrative, is_finished
        self.__lock_outputs = mp.Lock()

        # Initialise the selector
        self.__is_faulty = mp.Manager().list([False])
        self.__process = mp.Process(
            target=selector,
            args=(self.__inputs,
                  self.__outputs, self.__lock_outputs,
                  self.__is_faulty))

        # Begin processing
        self.__process.start()

    def stopSelector(self):
        """
        Forcibly terminate the selector process
        :return:
        """
        if self.is_finished is False:
            self.__process.terminate()
            self.is_finished = True

    def checkSelectorStatus(self):
        """
        Check the progress of the selector
        :return:
        """
        if self.is_finished is False:
            # If dead, then kill and forget
            if self.__is_faulty is True:
                self.stopSelector()

            # If not, check if it has completed
            else:
                with self.__lock_outputs:
                    if self.__outputs[-1] is True:
                        self.result_sphinx = self.__outputs[0]
                        self.result_google = self.__outputs[1]
                        self.selected_narrative = self.__outputs[2]
                        self.stopSelector()























