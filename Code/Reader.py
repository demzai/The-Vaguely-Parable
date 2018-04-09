"""
The code presented focuses on reading textual data to the user.
It provides a text to speech service as an independent process that can be killed at a moments notice.
The code here is intended to be called as a child process... thread safety rules apply.
Use protection, get consent, and play nice kids!
"""

# Dependencies:
import multiprocessing as mp
import win32com.client
import time
import os


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
        # noinspection SpellCheckingInspection
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Rate = 0

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
    except Exception as e:
        print('Reader has failed unexpectedly. {0}'.format(e))
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


