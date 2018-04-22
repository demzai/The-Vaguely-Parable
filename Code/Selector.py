"""
The code presented focuses on converting spoken words into textual data for further processing.
It provides a speech to text service that can  run independently from the rest of the system.
The code here is intended to be called as a child process... thread safety rules apply.
Use protection, get consent, and play nice kids!
"""

# Dependencies:
# @todo remove the try catch around a core multiprocessor function! (spawn_main in spawn.py)
# import Generate_Dictionary as gd
# import Sentence_Converter as sc
import Selection_Matching as sm
import speech_recognition as sr
import multiprocessing as mp
import pocketsphinx as ps
import traceback as t
import math
import time
import os


def recognise_sphinx(audio, dictionary=None):
    """
    Custom sphinx recogniser
    :param audio:
    :param dictionary:
    :return:
    """
    # Ensure audio is of the correct format
    assert isinstance(audio, sr.AudioData), "``audio_data`` must be audio data"
    # The included language models require audio to be 16-bit mono 16 kHz in little-endian format
    raw_data = audio.get_raw_data(convert_rate=16000, convert_width=2)

    # Create decoder object
    config = ps.Decoder.default_config()
    if dictionary is not None and os.path.isfile(dictionary):
        config.set_string("-dict", dictionary)
    elif dictionary is not None:
        with open("log_file.txt", "a") as log_file:
            log_file.write(str(t.format_exc()))
            log_file.write('WARNING: "{0}" WAS NOT FOUND'.format(dictionary))
        config.set_string("-dict", ps.get_model_path() + '\cmudict-en-us.dict')
    config.set_string("-hmm", ps.get_model_path() + '\en-us')
    config.set_string("-lm", ps.get_model_path() + '\en-us.lm.bin')
    # noinspection SpellCheckingInspection
    config.set_string("-logfn", os.devnull)
    decoder = ps.Decoder(config)

    # Obtain recognition results
    decoder.start_utt()  # Begin utterance processing
    # Process audio data with recognition enabled (no_search = False), as a full utterance (full_utt = True)
    decoder.process_raw(raw_data, False, True)
    decoder.end_utt()  # Stop utterance processing
    return decoder


def readSphinxData(sphinx_data, error):
    """
    Given an object returned from sphinx, convert it into a single result and its confidence level
    :param sphinx_data:
    :param error:
    :return:
    """
    return_value = ['', 0, error]
    if error != '' or sphinx_data is None or sphinx_data == []:
        return return_value

    try:
        top_10 = [[best.hypstr, best.score] for best, k in zip(sphinx_data.nbest(), range(10))]
        # segments = [seg.word for seg in sphinx_data.seg()]
        confidence = sphinx_data.get_logmath().exp(sphinx_data.hyp().prob)
        if confidence > 0:
            confidence = -1.0 / (math.log10(confidence) - 1)
        return_value = [top_10[0][0], confidence, error]  # [Top Result, Confidence, Error]
    except AttributeError:  # Figure out why this happens!
        pass
    return return_value


# noinspection PyBroadException
def readGoogleData(google_data, error):
    """
    Given an object returned from google, convert it into a single result and its confidence level
    :param google_data:
    :param error:
    :return:
    """
    result = ['', 0, error]
    try:
        if error == '' and google_data is not None and google_data != []:
            result = [google_data['alternative'][0]['transcript'],
                      google_data['alternative'][0]['confidence'],
                      error]  # [Top Result, Confidence, Error]
    except Exception as e:
        result = ['', 0, e]
    finally:
        return result


# noinspection PyUnusedLocal,PyBroadException
def getSphinxTranslation(audio, result, dictionary=None):
    """
    Given an audio snippet, and maybe some grammar, convert the speech into text using CMUsphinx
    :param audio:
    :param result:
    :type result: mp.Manager().list
    :param dictionary:
    :return:
    """
    translation = None
    error = ''
    try:
        converter = sr.Recognizer()

        # Translate with or without grammar
        if dictionary is not None:
            translation = recognise_sphinx(audio, dictionary=dictionary)
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
            try:
                result[i] = translation[i]
            except Exception:
                pass
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
    translation = None
    error = ''
    try:
        converter = sr.Recognizer()

        # Translate the audio into text
        translation = converter.recognize_google(audio, show_all=True)
        if not bool(translation):
            error = 'Bad Recognition'
    except sr.UnknownValueError:
        error = 'Bad Recognition'
    except Exception:
        error = 'Failed Server Request'
    finally:
        # Return only the information of interest
        translation = readGoogleData(translation, error)
        for i in range(3):
            try:
                result[i] = translation[i]
            except Exception:
                pass
        return result


# noinspection PyUnusedLocal, PyBroadException
def getWitApiTranslation(audio, result):
    """
    Given an audio snippet, and maybe some grammar, convert the speech into text using the Wit API
    :param audio:
    :param result:
    :type result: mp.Manager().list
    :return:
    """
    translation = ''
    error = ''
    try:
        converter = sr.Recognizer()

        # Translate the audio into text
        # noinspection SpellCheckingInspection
        translation = converter.recognize_wit(audio, key='2TW66CQWYNXUD3NE5B3BEGAJNDCZW27I')
        if not bool(translation):
            error = 'Bad Recognition'
    except sr.UnknownValueError:
        error = 'Bad Recognition'
    except Exception:
        error = 'Failed Server Request'
    finally:
        # Return only the information of interest
        if error == '':
            confidence = 0.7
        else:
            confidence = 0
        translation = [translation, confidence, error]
        for i in range(3):
            try:
                result[i] = translation[i]
            except Exception:
                pass
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
    process_id = os.getpid()
    # Throw everything inside of a try except loop to catch all errors
    try:
        # Extract the inputs
        audio = inputs[0]
        narratives = inputs[1]
        grammar_file = None
        dictionary_file = None
        regex_map = {}  # @todo double check if needed
        result_sphinx = ['', 0, '']
        result_google = ['', 0, '']
        result_witapi = ['', 0, '']

        # If the admin made a boo boo, then give him a firm warning
        narrative_names = []
        if isinstance(narratives, dict) is False and narratives is not None:
            raise TypeError('"narratives" IS NOT A MAP!')

        # Get grammars and regex's
        elif len(narratives) is not 0:
            # Get a list of narrative names
            narrative_names = list(narratives.keys())
            [grammar_file, regex_map] = sm.genGrammarForSelectionSet(narrative_names, process_id)
            # dictionary_file = sm.makeSubDictionary(narrative_names,
            #                                        str(sm.thesaurus_directory) + str(process_id) + '.dict')

        # Convert the audio using CMUsphinx (offline), Google, and WitAPI (online)
        if True:
            # @todo return to using google as a benchmark
            result_sphinx = mp.Manager().list(['', 0, ''])
            result_google = mp.Manager().list(['', 0, ''])
            result_witapi = mp.Manager().list(['', 0, ''])
            process_set = [mp.Process(target=getSphinxTranslation, args=(audio, result_sphinx, dictionary_file)),
                           mp.Process(target=getGoogleTranslation, args=(audio, result_google)),
                           mp.Process(target=getWitApiTranslation, args=(audio, result_witapi))]
            for i in range(len(process_set)):
                process_set[i].start()
            time.sleep(0.5)
            for i in range(len(process_set)):
                process_set[i].join()

            with lock_outputs:
                try:
                    outputs[0] = [x for x in result_google]
                except FileNotFoundError:
                    pass
                try:
                    outputs[1] = [x for x in result_witapi]
                except FileNotFoundError:
                    pass
                try:
                    outputs[2] = [x for x in result_sphinx]
                except FileNotFoundError:
                    pass

        # If the Google result gave a bad recognition error then ignore the whole thing
        if result_google[2] == 'Bad Recognition' or (sm.confidence_threshold > result_google[1] > 0.0):
            with lock_outputs:
                try:
                    outputs[2] = ['$Ignore', []]
                    outputs[-1] = True
                except FileNotFoundError:
                    pass
            return

        selection = sm.makeSelection([result_google, result_witapi, result_sphinx], narrative_names, regex_map)
        # with open("log_file.txt", "a") as log_file:
        #     log_file.write(str(narrative_names) + '\n' + str(regex_map))

        # Determine which narrative to select
        with lock_outputs:
            try:
                outputs[-2] = selection
                outputs[-1] = True
            except FileNotFoundError:
                pass
        return

    # On exception: print cause, or skip entirely
    except Exception as e:
        with open("log_file.txt", "a") as log_file:
            log_file.write(str(t.format_exc()))
            log_file.write('Selector Error: {0}\n'.format(e))

    # Ensure the faulty flag is raised on an error, no matter what
    finally:
        sm.cleanupExcessFiles(process_id)  # Remove excess file baggage
        is_faulty[0] = True


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
        self.result_google = ['', 0, '']
        self.result_witapi = ['', 0, '']
        self.result_sphinx = ['', 0, '']
        self.selected_narrative = ['', []]
        self.__outputs = mp.Manager().list(
            [[], [], [], [], False])  # Google, witapi, and sphinx results, selected narrative, is_finished
        self.__lock_outputs = mp.Lock()
        self.is_faulty = mp.Manager().list([False])

        # Initialise the selector
        self.__process = mp.Process(
            target=selector,
            args=(self.__inputs,
                  self.__outputs, self.__lock_outputs,
                  self.is_faulty))

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
            if self.__process.is_alive() and self.is_faulty is True:
                self.stopSelector()

            # If not, check if it has completed
            else:
                with self.__lock_outputs:
                    if self.__outputs[-1] is True:
                        # noinspection PyBroadException
                        try:
                            self.result_google = self.__outputs[0]
                            self.result_witapi = self.__outputs[1]
                            self.result_sphinx = self.__outputs[2]
                            self.selected_narrative = self.__outputs[-2]
                        except Exception:
                            pass
                        self.stopSelector()























