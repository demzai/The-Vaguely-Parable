"""
The code presented focuses on retrieving data to be read to the user.
It will act as a middle-man between the text to speech engine and the text-generator,
    handing the communications side of things.
The code here is intended to be called as a child process... thread safety rules
    apply.
Use protection, get consent, and play nice kids!
"""

import multiprocessing as mp
import winsound
import time
import os


def fakeReader(to_be_read, lock_to_be_read):
    """
    # Temporary place holder for the text to speech algorithm
    :param to_be_read: mp.Value(ct.c_char_p, '')
    :param lock_to_be_read: mp.Lock()
    :return: N/A
    """
    # Prove the reader exists by printing the passed parameters
    print(os.getpid())

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
                winsound.PlaySound('wrong.wav', winsound.SND_FILENAME)
                to_be_read[1] = False
        else:
            time.sleep(0.1)


def startReader():
    """
    # Initializer function for the reader
    :return: list
    """
    to_be_read = mp.Manager().list(['', False])
    lock_to_be_read = mp.Lock()

    process = mp.Process(
        target=fakeReader,
        args=(to_be_read, lock_to_be_read)
    )
    process.start()
    time.sleep(0.01)

    return [process, [to_be_read, lock_to_be_read]]


if __name__ == '__main__':
    while True:
        # Create a new reader
        [reader, to_read] = startReader()
        is_busy = True
        i = 0

        while i < 3:
            # Check if the reader is busy
            with to_read[1]:
                is_busy = to_read[0][1]

            # When not busy, ask for something new to be printed
            if is_busy is False:
                with to_read[1]:
                    to_read[0][0] = str(i)
                    to_read[0][1] = True
                is_busy = True
                i += 1
                time.sleep(0.1)

        # Kill the process before repeating!
        reader.terminate()

