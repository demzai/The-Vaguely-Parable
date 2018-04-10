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
        # recorder.energy_threshold = 500  # 10 to 25?
        with sr.Microphone() as source:
            while True:
                with lock_user_input:
                    should_wait = user_input[-1]
                # @todo remove non-listening period
                # @todo live-stream audio data
                # @todo manually check if user is talking?
                # If the main process isn't busy processing the previous input, then listen for use instructions
                if should_wait is False:
                    print("Please speak when ready.")
                    # audio = input()  # @todo revert back to audio input
                    audio = recorder.listen(source)
                    timestamp = time.time()
                    with lock_user_input:
                        user_input[0] += [[audio, timestamp]]
                        user_input[-1] = True
                # Otherwise, wait patiently for the main process to finish
                else:
                    time.sleep(0.1)
    except Exception as e:
        is_faulty[0] = True
        print('Listener has failed unexpectedly. {0}'.format(e))
    finally:
        is_faulty[0] = True


class ListenerObj:
    """
    Object used to simplify the interface with the listener object
    """
    def __init__(self):
        """
        # Initializer function for the listener class
        :return: list
        """
        self.should_listen = False
        self.alive = False
        self.user_inputs = []
        self.__stack = []
        self.__user_input = mp.Manager().list([[], False])  # [list of [audio, timestamp], has_new_input]
        self.__is_faulty = mp.Manager().list([False])
        self.__lock_user_input = mp.Lock()
        self.__process = None

    def startListener(self):
        """
        # Initializer function for the listener
        :return: list
        """
        self.__user_input[0] = None  # audio
        self.__user_input[1] = 0.0  # timestamp
        self.__user_input[2] = False  # has_new_input
        self.__is_faulty[0] = False
        self.__lock_user_input = mp.Lock()

        process = mp.Process(
            target=listener,
            args=(self.__user_input, self.__lock_user_input, self.__is_faulty)
        )
        process.start()
        self.alive = True

    def stopListener(self):
        """
        Forcibly kill the listener if it is running
        :return:
        """
        if self.alive is True:
            self.__process.terminate()
            self.alive = False

    def __restartListener(self):
        """
        Restarts the Listener
        :return:
        """
        self.stopListener()
        self.startListener()

    def __updateAliveStatus(self):
        """
        Determines whether the listener should be active or not
        :return:
        """
        # Check whether the listener has crashed
        if self.alive is True and self.__is_faulty[0] is True:
            self.__restartListener()

        # If there's work to be done and the listener is dead, start it up
        if self.should_listen is True and self.alive is False:
            self.startListener()

        # If the listener shouldn't be listening
        elif self.should_listen is False and self.alive is True:
            self.stopListener()

    def checkListenerStatus(self):
        """
        Checks whether there's been an error within the listener and rectifies it if possible
        :return:
        """
        # Resolve (in)active status issues
        self.__updateAliveStatus()

        # Check if the listener has made another recording
        with self.__lock_user_input:
            has_new_input = self.__user_input[-1]
            if has_new_input is True:
                self.__stack += self.__user_input[0]

        # Check if there are any recordings in need of processing
        a = 1

    def dumpStack(self):
        """
        Deletes the contents of the stack
        :return:
        """
        self.__stack = []
























