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
import Code_Interpreter as ci
import traceback as t
# import winsound


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
        speaker.Rate = 3

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
        with open("log_file.txt", "a") as log_file:
            log_file.write(str(t.format_exc()))
            log_file.write('Reader has failed unexpectedly. {0}\n'.format(e))
    finally:
        try:
            is_faulty[0] = True
        except FileNotFoundError:
            pass


def getNextText(stack):
    """
    # Reads the narrative pointed to by the current address
    """
    i = 0
    output = None
    for text in stack:
        i += 1
        if text[0] == 'Text':
            output = str(text[1])
            break
        elif text[0] == 'Container':
            output = str(ci.parseContainerCode(text[1], text[2]))
            break
        elif text[0] == 'Code' or text[0] == 'Variable':
            ci.interpretCode(text[2][0])
        elif text[0] == 'Segment':
            ci.interpretCode(text[2][0])
    return [output, stack[i:]]


class ReaderObj:
    """
    Object used to handle interactions with the reader
    """
    def __init__(self):
        """
        # Initializer function for the reader class
        :return: list
        """
        self.stack = []
        self.interruptable = True
        self.alive = False
        self.is_busy = False
        self.__to_be_read = mp.Manager().list(['', False])
        self.__is_faulty = mp.Manager().list([False])
        self.__lock_to_be_read = mp.Lock()
        self.__process = self.__process = mp.Process(
                target=reader,
                args=(self.__to_be_read, self.__lock_to_be_read, self.__is_faulty)
            )

    def startReader(self):
        """
        Starts the reader process
        :return:
        """
        if self.alive is False:
            self.__to_be_read[0] = ''
            self.__to_be_read[1] = False
            self.__is_faulty[0] = False
            self.__lock_to_be_read = mp.Lock()
            self.__process = mp.Process(
                target=reader,
                args=(self.__to_be_read, self.__lock_to_be_read, self.__is_faulty)
            )
            self.__process.start()
            self.alive = True

    def stopReader(self):
        """
        Force kill the reader if it is running
        :return:
        """
        if self.alive is True:
            if self.interruptable is True or self.is_busy is False:
                self.__stopReader()
                return True
            else:
                return False

    def __stopReader(self):
        """
        Forcibly kill the reader if it is running
        :return:
        """
        if self.alive is True:
            self.__process.terminate()
            self.alive = False

    def __restartReader(self):
        """
        Restarts the reader
        :return:
        """
        self.__stopReader()
        self.startReader()

    def checkReaderStatus(self):
        """
        Checks whether there's been an error within the reader and rectifies it if possible
        :return:
        """
        self.alive = self.__process.is_alive()
        # Check whether the reader has crashed
        if self.alive is True and self.__is_faulty[0] is True:
            self.__restartReader()

        # If there's work to be done and the reader is dead, start it up
        if len(self.stack) is not 0 and self.alive is False:
            self.startReader()

        # Update the readers busy status
        with self.__lock_to_be_read:
            self.is_busy = self.__to_be_read[1]

        # If alive and not busy
        if self.alive is True and self.is_busy is False:
            # If no work then kill it
            if len(self.stack) is 0:
                self.stopReader()
            # If there's work left to do then get the next chunk for processing
            else:
                with self.__lock_to_be_read:
                    [self.__to_be_read[0], self.stack] = getNextText(self.stack)
                    if self.__to_be_read[0] is None:
                        self.__stopReader()
                    else:
                        self.__to_be_read[1] = True
                        self.is_busy = True

    def dumpStack(self):
        """
        Deletes the contents of the stack
        :return:
        """
        self.stack = []

