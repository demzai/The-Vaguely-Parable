"""
The code presented focuses on retrieving audio spoken by the user.
It provides a listen when spoken to service that can run independently from the rest of the system.
The code here is intended to be called as a child process... thread safety rules apply.
Use protection, get consent, and play nice kids!
"""

# Dependencies:
import speech_recognition as sr
import multiprocessing as mp
import time


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
        recorder.energy_threshold = 15  # 10 to 25?
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
