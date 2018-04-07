"""
# This is the testing ground.
# Develop functions here, but do not leave them here!
# This is a glorified playground to make a mess in!
"""

# Dependencies:
import speech_recognition as sr
import multiprocessing as mp
import win32com.client
import time
import os


def resetChildProcess(curr_process, creator_function):
    """
    Forcibly kill off a given child process and replace it with a new one
    :param curr_process:
    :param creator_function:
    :return:
    """
    curr_process.terminate()
    return creator_function()


# noinspection PyBroadException
def reader(to_be_read, lock_to_be_read, is_faulty):
    """
    # Temporary place holder for the text to speech algorithm
    :param to_be_read:
    :param lock_to_be_read:
    :param is_faulty:
    :return:
    """
    try:
        # Prove the reader exists by printing the passed parameters
        print(os.getpid())
        # noinspection SpellCheckingInspection
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Rate = 0
        speaker.Voice = speaker.GetVoices().Item(1)

        # Continue indefinitely until terminated
        while True:
            # Check whether something needs to be done
            with lock_to_be_read:
                has_changed = to_be_read[1]

            # If new text is available, then display / say it
            if has_changed is True:
                with lock_to_be_read:
                    string = to_be_read[0]
                print(string)
                speaker.Speak(string)
                # winsound.PlaySound('wrong.wav', winsound.SND_FILENAME)
                with lock_to_be_read:
                    to_be_read[1] = False
            else:
                time.sleep(0.1)
    except Exception:
        print('Reader has failed unexpectedly.')
    finally:
        is_faulty[0] = True


def startReader():
    """
    # Initializer function for the reader
    :return: list
    """
    to_be_read = mp.Manager().list(['', False])
    is_faulty = mp.Manager().list([False])
    lock_to_be_read = mp.Lock()

    process = mp.Process(
        target=reader,
        args=(to_be_read, lock_to_be_read, is_faulty)
    )
    process.start()

    return [process, [to_be_read, lock_to_be_read], is_faulty]


# noinspection PyBroadException
def listener(user_input, lock_user_input, is_faulty):
    """
    # Waits for user input, and provides the audio transcript of that input
    :param user_input:
    :param lock_user_input:
    :param is_faulty:
    :return:
    """
    try:
        recorder = sr.Recognizer()
        with sr.Microphone() as source:
            while True:
                with lock_user_input:
                    should_wait = user_input[-1]
                # If the main process isn't busy processing the previous input, then listen for use instructions
                if should_wait is False:
                    print("Please speak when ready.")
                    audio = recorder.listen(source)
                    timestamp = time.time()
                    with lock_user_input:
                        user_input[0] = audio
                        user_input[1] = timestamp
                        user_input[-1] = True
                # Otherwise, wait patiently for the main process to finish
                else:
                    time.sleep(0.1)
    except Exception:
        print('Listener has failed unexpectedly.')
        is_faulty[0] = True


def startListener():
    """
    # Initializer function for the listener
    :return: list
    """
    user_input = mp.Manager().list([None, 0.0, False])  # audio, timestamp, has_new_input
    is_faulty = mp.Manager().list([False])
    lock_user_input = mp.Lock()

    process = mp.Process(
        target=listener,
        args=(user_input, lock_user_input, is_faulty)
    )
    process.start()

    return [process, [user_input, lock_user_input], is_faulty]


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
        use_google = True
        while True:
            with lock_inputs:
                is_work_to_do = inputs[-1]
            if is_work_to_do is True:
                # Returns 10 best estimates, along with more detailed info for the best result
                converter = sr.Recognizer()
                resultG = None
                with lock_inputs:
                    if use_google is True:
                        try:
                            resultG = [[converter.recognize_google(inputs[0], show_all=False)]]
                        except Exception:
                            use_google = False
                            print('I take exception to that!')
                    if use_google is False:
                        resultS = converter.recognize_sphinx(inputs[0], show_all=True)
                if use_google is False:
                    top_10 = [[best.hypstr, best.score] for best, k in zip(resultS.nbest(), range(10))]
                    segments = [seg.word for seg in resultS.seg()]
                    confidence = resultS.get_logmath().exp(resultS.hyp().prob)
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


def main():
    """
    The main function!
    :return:
    """
    [listen, user_input, is_listen_faulty] = startListener()
    [select, selector_inputs, selector_results, is_select_faulty] = startSelector()
    [read, to_be_read, is_reader_faulty] = startReader()

    try:
        prev_state = [False, False, False]
        while True:
            # Ensure that the listener and reader processes are fully functional
            if is_listen_faulty is True:
                [listen, user_input, is_listen_faulty] = resetChildProcess(listen, startListener)
            if is_select_faulty is True:
                [select, selector_inputs, selector_results, is_select_faulty] = resetChildProcess(select, startSelector)
            if is_reader_faulty is True:
                [read, to_be_read, is_reader_faulty] = resetChildProcess(read, startReader)

            # Check the status of the listener
            with user_input[1]:
                # If the listener has picked something up...
                if user_input[0][-1] is True and prev_state[0] is False:
                    # Set the selector running - assumes it isn't already based on the rest of the logic
                    with selector_inputs[1]:
                        selector_inputs[0][0] = user_input[0][0]
                        selector_inputs[0][-1] = True
                    prev_state[0] = True
                # If not, then never mind
                else:
                    pass

            # Check the status of the selector and reader
            with selector_inputs[1] and to_be_read[1]:
                is_selector_busy = selector_inputs[0][-1]
                is_reader_reading = to_be_read[0][-1]

            # Otherwise, if the selector is busy, then the user is probably waiting for a response.
            if is_selector_busy is True and is_reader_reading is False:
                # Play some filler inflexions whilst the user waits (hmm...)
                prev_state[1] = True
                with to_be_read[1]:
                    to_be_read[0][0] = 'Hmm hmm hmm... Um... Uhh... '*5
                    to_be_read[0][-1] = True

            # If the selector has just finished
            elif is_selector_busy is False and prev_state[1] is True:
                # If the reader is currently reading, then forcibly stop it so it can say the important stuff
                if is_reader_reading is True:
                    [read, to_be_read, is_reader_faulty] = resetChildProcess(read, startReader)
                # Play the next thing (in this case, repeat what the computer thinks the user just said back to them
                with selector_results[1] and to_be_read[1]:
                    print(str(selector_results[0][0][0]))
                    to_be_read[0][0] = selector_results[0][0][0][0]
                    to_be_read[0][-1] = True
                prev_state[1] = False
                prev_state[2] = True

            # If the reader has just finished reading...
            elif is_reader_reading is False and prev_state[2] is True:
                # Restart the listener
                with user_input[1]:
                    user_input[0][-1] = False
                prev_state[0] = False
                prev_state[2] = False

    finally:
        listen.terminate()
        select.terminate()
        read.terminate()


if __name__ == '__main__':
    main()
