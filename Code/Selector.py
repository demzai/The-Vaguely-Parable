"""
The code presented focuses on converting spoken words into textual data for further processing.
It provides a speech to text service that can  run independently from the rest of the system.
The code here is intended to be called as a child process... thread safety rules apply.
Use protection, get consent, and play nice kids!
"""

# Dependencies:
import speech_recognition as sr
import multiprocessing as mp
import time


# noinspection PyBroadException
def selector(inputs, lock_inputs, outputs, lock_outputs, is_faulty):
    """
    Takes collected audio and converts it into text.
    Future versions may also select a narrative state.
    :param inputs:
    :param lock_inputs:
    :param outputs:
    :param lock_outputs:
    :param is_faulty:
    :return:
    """
    # Offline translation using CMUSphinx:
    try:
        converter = sr.Recognizer()
        use_google = False
        while True:
            with lock_inputs:
                is_work_to_do = inputs[-1]
            if is_work_to_do is True:
                # Returns 10 best estimates, along with more detailed info for the best result
                resultG = None
                resultS = None
                with lock_inputs:
                    if use_google is True:
                        try:
                            resultG = [[converter.recognize_google(inputs[0], show_all=False)]]
                        except Exception:
                            use_google = False
                            print('I take exception to that!')
                    if use_google is False:
                        resultS = converter.recognize_sphinx(inputs[0], show_all=False,
                                                             grammar='Grammars/donotgoanywhere.gram')
                        print(str(resultS))
                if use_google is False:
                    top_10 = [['Hello World']]
                    segments = None
                    confidence = None
                    # top_10 = [[best.hypstr, best.score] for best, k in zip(resultS.nbest(), range(10))]
                    # segments = [seg.word for seg in resultS.seg()]
                    # confidence = resultS.get_logmath().exp(resultS.hyp().prob)
                else:
                    top_10 = resultG
                    segments = None
                    confidence = None
                use_google = True

                # Stores the results for the parent to interpret
                with lock_outputs:
                    outputs[0] = top_10
                    outputs[1] = segments
                    outputs[2] = confidence
                with lock_inputs:
                    inputs[-1] = False
            else:
                time.sleep(0.1)

    # Resolve exceptions
    except sr.UnknownValueError:
        print("Sphinx could not understand audio")
        is_faulty[0] = True
    except sr.RequestError as e:
        print("Sphinx error; {0}".format(e))
        is_faulty[0] = True
    except Exception:
        print('Selector has failed unexpectedly.')
        is_faulty[0] = True


def startSelector():
    """
    # Initializer function for the selector
    :return:
    """
    inputs = mp.Manager().list([None, None, False])  # audio, narrative_options, is_work_to_do
    lock_inputs = mp.Lock()
    outputs = mp.Manager().list([None, None, None])  # top_10, segmented_best, confidence_best
    lock_outputs = mp.Lock()

    is_faulty = mp.Manager().list([False])

    process = mp.Process(
        target=selector,
        args=(inputs, lock_inputs, outputs, lock_outputs, is_faulty)
    )
    process.start()

    return [process, [inputs, lock_inputs], [outputs, lock_outputs], is_faulty]
